atlas {
  name = "mafrosis/ogre-staging"
}
provider "aws" {
  access_key = "${var.AWS_ACCESS_KEY}"
  secret_key = "${var.AWS_SECRET_KEY}"
  region = "${var.region}"
}

resource "aws_security_group" "default" {
  name = "ogre staging"
  description = "OGRE staging"

  # SSH access from anywhere
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # http access from anywhere
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # https access from anywhere
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # open 8233 for pypiserver
  ingress {
    from_port = 8233
    to_port = 8233
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "atlas_artifact" "ogre-staging" {
  name = "mafrosis/ogre-staging"
  type = "amazon.ami"
  version = "${var.version}"
}

resource "null_resource" "local-software" {
  # install awscli on the Atlas provisioning machine
  provisioner "local-exec" {
    command = <<EOH
      if [ $(uname) = 'Darwin' ]; then
        brew install awscli
      else
        sudo apt-get update && sudo apt-get install -y awscli
      fi
EOH
  }

  # re-run this everytime the AMI id has changed
  triggers {
    ami = "${atlas_artifact.ogre-staging.metadata_full.region-eu-west-1}"
  }
}

resource "aws_instance" "ogre-staging" {
  ami = "${atlas_artifact.ogre-staging.metadata_full.region-eu-west-1}"
  instance_type = "t2.micro"

  security_groups = ["${aws_security_group.default.name}"]
  key_name = "ogre-staging"

  tags {
    Name = "ogre-staging"
  }

  user_data = "#!/bin/bash\n/usr/local/bin/acmetool --batch reconcile && systemctl restart nginx"

	# associate EIP to the EC2 instance
  provisioner "local-exec" {
    command = <<EOH
      AWS_ACCESS_KEY_ID='${var.AWS_ACCESS_KEY}' \
      AWS_SECRET_ACCESS_KEY='${var.AWS_SECRET_KEY}' \
      AWS_DEFAULT_REGION='${var.region}' \
      aws ec2 associate-address --instance-id ${aws_instance.ogre-staging.id} --allocation-id ${var.eip}
EOH
  }
}
