resource "spacelift_aws_integration" "aws" {
  name                           = "AWS - Nova Install"
  generate_credentials_in_worker = false
  role_arn                       = "arn:aws:iam::393035998875:role/spacelift-oidc-role"
  duration_seconds               = 3600
  region                         = var.aws_region
  space_id                       = "root"
  labels = [
    "autoattach:aws",
  ]
  autoattach_enabled = true
}

resource "spacelift_space" "nova" {
  name             = "nova"
  parent_space_id  = "root"
  description      = "Nova root space"
  inherit_entities = true
  labels = [
    "nova",
    "root"
  ]
}

resource "spacelift_space" "children" {
  for_each         = local.spacelift_child_spaces
  parent_space_id  = spacelift_space.nova.id
  name             = each.value.name
  description      = each.value.description
  inherit_entities = true
  labels = [
    "nova",
    each.key
  ]
}

resource "spacelift_context" "contexts" {
  for_each     = local.contexts
  name         = each.key
  description  = each.value.description
  labels       = ["autoattach:${each.key}"]
  before_init  = try(each.value.before_init, [])
  before_apply = try(each.value.before_apply, [])
}

resource "spacelift_environment_variable" "context_vars" {
  for_each = local.environment_vars

  context_id = spacelift_context.contexts[each.value.ctx_key].id
  name       = each.value.name
  value      = each.value.value
  write_only = false
}

resource "spacelift_mounted_file" "context_scripts" {
  for_each = local.context_mounted_files

  context_id    = spacelift_context.contexts[each.value.ctx_key].id
  relative_path = each.value.relative_path
  content       = filebase64(each.value.source_path)
  write_only    = false
}

resource "spacelift_stack" "stacks" {
  for_each = local.spacelift_stacks
  github_enterprise {
    id        = "github"
    namespace = "NOVA-Install"
  }
  name                             = each.key
  project_root                     = each.value.project_root
  branch                           = "main"
  repository                       = "NOVA_Installer_OS"
  space_id                         = local.spacelift_space_ids[each.value.space_key]
  enable_sensitive_outputs_upload  = true
  enable_well_known_secret_masking = true
  allow_run_promotion              = false
  terraform_smart_sanitization     = true
  enable_local_preview             = true
  protect_from_deletion            = true
  terraform_version                = ">= 1.11.0"
  terraform_workflow_tool          = "OPEN_TOFU"
  labels = concat(
    [
      "nova",
      "nova-${each.value.space_key}",
    ],
    each.value.labels
  )
}

resource "spacelift_stack_dependency" "dependencies" {
  for_each = local.spacelift_stacks_dependencies_flat

  stack_id            = spacelift_stack.stacks[each.value.stack_key].id
  depends_on_stack_id = spacelift_stack.stacks[each.value.depends_on].id
}

resource "spacelift_stack_dependency_reference" "references" {
  for_each = local.dependency_references

  stack_dependency_id = spacelift_stack_dependency.dependencies[each.value.stack_dependency_id].id
  input_name          = each.value.input_name
  output_name         = each.value.output_name
}
