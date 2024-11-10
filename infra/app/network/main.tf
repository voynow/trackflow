# Define provider
provider "aws" {
  region = var.region
  default_tags {
    tags = {
      app = var.app_name
    }
  }
}

# Create VPC and IGW
resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr_block
}
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}

# Create public subnets
resource "aws_subnet" "public_subnets" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.public_cidr_blocks[count.index]
  availability_zone = var.availability_zones[count.index]
}

# Create routing tables for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }
}
resource "aws_route_table_association" "publics" {
  count          = length(var.availability_zones)
  subnet_id      = element(aws_subnet.public_subnets.*.id, count.index)
  route_table_id = aws_route_table.public.id
}
