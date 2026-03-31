---
name: terraform-stack
description: Create, modify, or wire up Terraform stacks in this monorepo's infra/stacks/ directory. Use this skill whenever the user asks to add a new Terraform stack, add resources to an existing stack, wire up Spacelift dependencies, create a new environment for an existing stack, or modify the Spacelift locals.tf configuration. Also trigger when the user mentions NLBs, ECS services, VPCs, or other AWS infrastructure that lives in infra/stacks/.
---

# Terraform Stack Management

This project uses Terraform with Spacelift for infrastructure orchestration. All infrastructure lives under `infra/stacks/` with a consistent structure.

## Directory layout

```
infra/stacks/<stack-name>/<environment>/
  locals.tf      # Derived values, helper expressions
  providers.tf   # Terraform + provider config with Spacelift role assumption
  variables.tf   # Input variables (injected by Spacelift contexts + dependencies)
  main.tf        # Resources
  outputs.tf     # Values consumed by downstream stacks
```

Not every stack needs all five files — `locals.tf` and `outputs.tf` can be omitted if empty — but this is the standard set.

## Providers

Every AWS stack assumes a Spacelift-managed IAM role and applies default tags. Only include providers the stack actually uses.

```hcl
terraform {
  required_version = ">= 1.11.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.6.0"
    }
    # Add github provider if the stack reads releases.json or sets GitHub Actions variables
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_runtime_regions[0]
  assume_role {
    role_arn = var.aws_spacelift_role_arn
  }
  default_tags {
    tags = {
      Stack       = "<stack-name>"
      Environment = var.environment
      Product     = var.product
    }
  }
}
```

The GitHub provider is configured via `GITHUB_TOKEN` env var (injected by the `github` label in Spacelift), so it needs no explicit config block — just the `required_providers` entry.

## Variables

Every AWS stack receives these base variables from Spacelift contexts (they auto-attach via labels):

```hcl
variable "aws_runtime_regions" { type = list(string) }
variable "aws_spacelift_role_arn" { type = string }
variable "environment" {
  type = string
  validation {
    condition     = contains(["prd", "stg", "dev"], var.environment)
    error_message = "Environment must be prd, stg, or dev."
  }
}
variable "product" { type = string }
```

Additional variables come from stack dependencies (see Spacelift wiring below). Common patterns:

- **VPC networking** (from `vpc-stg`): `private_subnets_by_region`, `public_subnets_by_region`, `vpc_cidr_blocks_by_region`, `vpc_ids_by_region` — all `map(...)` types
- **NLB target groups** (from `network-load-balancer-*`): `<service>_target_group_arn` as `string`
- **ECR access**: `aws_account_id` as `string`
- **GitHub reads**: `github_token` (sensitive), `environment_branch` (e.g. `env-prd`)

Mark secrets with `sensitive = true`.

## Spacelift wiring

All Spacelift configuration lives in `infra/stacks/spacelift/shared/locals.tf`. After creating stack files, register the stack there.

### 1. Register the stack

Add an entry to the `spacelift_stacks` map. The key is `<stack-name>-<env>`:

```hcl
"<stack-name>-<env>" = {
  project_root = "infra/stacks/<stack-name>/<env>"
  space_key    = "<env>"       # prd, stg, or shared
  labels       = ["aws"]       # controls which contexts auto-attach
}
```

**Labels** determine which Spacelift contexts attach to the stack. Common labels:
- `"aws"` — attaches the AWS provider context (role ARN, regions, account ID)
- `"github"` — attaches GITHUB_TOKEN for GitHub provider access
- `"99dot5-contentful"` — attaches Contentful-specific config + install hooks
- `"99dot5-supabase-shared"`, `"99dot5-supabase-prd"` — Supabase config

### 2. Wire dependencies

If the stack consumes outputs from other stacks, add an entry to `spacelift_stacks_dependencies`. Each dependency lists the upstream stack and maps its output names to `TF_VAR_` input names:

```hcl
"<stack-name>-<env>" = [
  {
    depends_on = "<upstream-stack-key>",
    references = {
      "<output_name>" : "TF_VAR_<variable_name>"
    }
  }
]
```

The dependency chain typically flows: `vpc` -> `network-load-balancer` -> `services-*`. For example, `services-sequencer-prd` depends on both `vpc-stg` (for networking) and `network-load-balancer-prd` (for the target group ARN).

A stack can have multiple dependencies — just add more objects to the list. Each object is one upstream stack.

## Environments and accounts

| Environment | Account ID     | Spacelift context |
|-------------|----------------|-------------------|
| prd         | 183300739714   | 99dot5-prd        |
| stg         | 172177042848   | 99dot5-stg        |
| shared      | 478860598407   | 99dot5-shared     |

Spacelift contexts inject `TF_VAR_aws_account_id`, `TF_VAR_aws_runtime_regions`, `TF_VAR_aws_spacelift_role_arn`, and `TF_VAR_environment` automatically based on the stack's `space_key`.

## Modules

Most resource logic belongs in a reusable module under `infra/modules/<module-name>/`, not in the stack itself. Stacks should be thin wrappers that instantiate modules and pass variables through.

```
infra/modules/<module-name>/
  providers.tf   # required_providers only (no provider config — inherited from caller)
  variables.tf   # inputs the module needs
  locals.tf      # internal logic (CIDR math, lookups, etc.)
  main.tf        # the actual resources
  outputs.tf     # values the calling stack can reference
```

The module name should match the stack name when there's a 1:1 relationship (e.g. `infra/modules/vpc` is called by `infra/stacks/vpc/`).

### Module providers.tf

Modules declare `required_providers` but do not configure them — provider configuration is inherited from the calling stack:

```hcl
terraform {
  required_version = ">= 1.11.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.6.0"
    }
  }
}
```

### Calling a module from a stack

The stack's `main.tf` should be minimal — just module calls and any glue resources that don't belong in the module. Modules are referenced with a relative path:

```hcl
module "<module_name>" {
  for_each = toset(var.aws_runtime_regions)

  source      = "../../../modules/<module-name>"
  aws_region  = each.value
  environment = var.environment
  product     = var.product
  # ... other variables
}
```

The `for_each` over regions is the standard multi-region pattern. For stacks that only target one region, you can still use `for_each` for consistency, or call the module directly.

When a module needs data from upstream stacks (VPC IDs, subnets), pass them through from the stack's variables using the region key:

```hcl
module "my_service" {
  for_each = toset(var.aws_runtime_regions)

  source    = "../../../modules/my-service"
  vpc_id    = var.vpc_ids_by_region[each.value]
  subnet_id = var.public_subnets_by_region[each.value][0]
  # ...
}
```

### Stack outputs from modules

When a stack calls a module with `for_each`, outputs should be region-keyed maps so downstream stacks can consume them by region:

```hcl
output "vpc_ids_by_region" {
  value = { for region, mod in module.vpc : region => mod.vpc_id }
}
```

## Multi-region pattern

The VPC stack deploys resources per region using `for_each = toset(var.aws_runtime_regions)` and outputs region-keyed maps (e.g. `public_subnets_by_region`). Downstream stacks that only need one region extract it with the region key in locals:

```hcl
locals {
  region = var.aws_runtime_regions[0]
}
```

## IAM resources

**Do NOT create IAM resources (roles, policies, policy attachments, instance profiles, etc.) inside Terraform stacks or modules.** IAM is managed externally via CloudFormation. When a stack needs IAM roles or policies, output a message to the user listing the required IAM resources — including role names, trust policies, and managed policy ARNs — so they can be created through the external IAM process.

To reference IAM role ARNs, use a `data "aws_cloudformation_export"` lookup against the management account rather than passing them as variables. This requires an additional `aws.management` provider alias:

```hcl
variable "management_aws_region" { type = string }

provider "aws" {
  alias  = "management"
  region = var.management_aws_region
  assume_role {
    role_arn = var.aws_spacelift_role_arn
  }
  default_tags {
    tags = {
      Stack       = "<stack-name>"
      Environment = var.environment
      Product     = var.product
    }
  }
}
```

Then look up the exported role ARN:

```hcl
data "aws_cloudformation_export" "my_role_arn" {
  provider = aws.management
  name     = "GlobalManagementStack-<RoleName>Arn"
}
```

Use `data.aws_cloudformation_export.my_role_arn.value` wherever the role ARN is needed (e.g. `execution_role_arn`, `task_role_arn`).

## Releases and versioning

Service stacks that deploy containers or AMIs read version info from `releases.json` in the repo (on an environment-specific branch like `env-prd`). The pattern uses the GitHub provider:

```hcl
data "github_repository_file" "releases" {
  repository = "99dot5"
  branch     = var.environment_branch
  file       = "env/releases.json"
}

locals {
  releases      = jsondecode(data.github_repository_file.releases.content)
  container_tag = local.releases.services.<service_name>.version
}
```

This requires the `github` label on the stack and `github_token` + `environment_branch` variables.

## Shared Resources

There is a shared environment that contains all container images and other resources that are used by all other environments. This is the `shared` environment.

## Style Guide

- Create an empty outputs.tf file in every stack directory, even if it's empty.
- Add descriptions to all variables and outputs
- Do not create variables that are never used
