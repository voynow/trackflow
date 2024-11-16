output "vpc" {
  value = aws_vpc.this
}

output "public_subnets" {
  value = aws_subnet.public_subnets
}