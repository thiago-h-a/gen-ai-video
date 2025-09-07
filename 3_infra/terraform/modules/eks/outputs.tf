
output "cluster_name"    { value = local.enabled ? aws_eks_cluster.this[0].name : null }
output "cluster_endpoint" { value = local.enabled ? aws_eks_cluster.this[0].endpoint : null }
output "oidc_issuer"      { value = local.enabled ? aws_eks_cluster.this[0].identity[0].oidc[0].issuer : null }
