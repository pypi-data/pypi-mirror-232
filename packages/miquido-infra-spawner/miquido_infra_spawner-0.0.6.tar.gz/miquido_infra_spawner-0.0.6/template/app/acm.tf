module "acm_alb" {
  source = "git::https://github.com/miquido/terraform-acm-request-certificate.git?ref=tags/3.0.6"

  providers = {
    aws.acm = aws
    aws.dns = aws
  }

  domain_name                 = local.ecs_service_domain
  ttl                         = "300"
  subject_alternative_names   = []
  hosted_zone_id              = var.route53_zone_id

  wait_for_certificate_issued = true
  tags                        = var.tags
}

resource "time_sleep" "wait_30_seconds" {
  depends_on = [module.acm_alb.aws_acm_certificate_validation]

  create_duration = "30s"
}

resource "aws_lb_listener_certificate" "default" {
  listener_arn    = var.https_listener_arn
  certificate_arn = module.acm_alb.arn
  depends_on = [time_sleep.wait_30_seconds]
}