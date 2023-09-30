provider "aws" {
  region = "eu-central-1"
  assume_role {
    role_arn = "arn:aws:iam::230562640235:role/AdministratorAccess"
  }
}
