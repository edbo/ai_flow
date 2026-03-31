locals {
  account_ids = {
    "prd" = "964993352427"
  }
  contexts = {
    "ai-flow" = {
      description = "AI Flow Root Context"
      variables = {
        TF_VAR_product         = "ai-flow"
        TF_VAR_repository_name = "ai_flow"
      }
    }
    "ai-flow-prd" = {
      description = "AI Flow Production Context"
      variables = {
        TF_VAR_aws_account_id = local.account_ids["prd"],
      }
    }
    "temporal" = {
      description = "Temporal context"
      variables   = {}
    }
  }
  environment_vars = merge([
    for ctx_key, ctx in local.contexts : (
      length(try(keys(ctx.variables), [])) > 0 ? {
        for var_key, var_value in ctx.variables :
        "${ctx_key}:${var_key}" => {
          ctx_key = ctx_key
          name    = var_key
          value   = try(tostring(var_value), jsonencode(var_value))
        }
      } : {}
    )
  ]...)

  context_mounted_files = {
    # "ai-flow:install-script" = {
    #   ctx_key       = "ai-flow-contentful"
    #   relative_path = "scripts/install-contentful-provider.sh"
    #   source_path   = "${path.module}/scripts/install-contentful-provider.sh"
    # }
  }

  spacelift_child_spaces = {
    ai-flow-prd = {
      name        = "ai-flow-prd"
      description = "AI Flow production space"
    }
  }

  spacelift_space_ids = {
    prd = spacelift_space.children["ai-flow-prd"].id
  }

  spacelift_stacks = {
    "ai-flow-api-prod" = {
      project_root = "infra/stacks/api/prd"
      space_key    = "prd"
      labels       = ["aws"]
    }
  }

  spacelift_stacks_dependencies = {
  }

  # Flatten the dependencies structure for use in resources
  spacelift_stacks_dependencies_flat = merge([
    for stack_key, dependencies in local.spacelift_stacks_dependencies : {
      for idx, dep in dependencies :
      "${stack_key}:${dep.depends_on}" => {
        stack_key  = stack_key
        depends_on = dep.depends_on
        references = dep.references
      }
    }
  ]...)

  dependency_references = merge([
    for dep_key, dep in local.spacelift_stacks_dependencies_flat : (
      length(try(keys(dep.references), [])) > 0 ? {
        for var_key, var_value in dep.references :
        "${dep_key}:${var_key}" => {
          stack_dependency_id = dep_key
          input_name          = var_value
          output_name         = var_key
        }
      } : {}
    )
  ]...)
}
