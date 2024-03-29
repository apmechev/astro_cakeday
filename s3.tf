resource "aws_s3_bucket" "site_bucket" {
  bucket = local.frontend_bucket_name
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags = {
    Project = "Cakedays"
    Prefix  = local.prefix
    Branch  = var.branch_name
  }

  force_destroy = true
}

resource "aws_s3_bucket" "bakery_bucket" {
  bucket = local.bakery_bucket_name
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["https://${local.frontend_bucket_name}", "http://${local.frontend_bucket_name}"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }

  tags = {
    Project = "Cakedays"
    Prefix  = local.prefix
  }

  force_destroy = true
}

######### Policies

resource "aws_s3_bucket_policy" "bakery_bucket_policy" {
  bucket = aws_s3_bucket.bakery_bucket.id

  policy = jsonencode(
    {
      Version = "2012-10-17",
      Statement = [
        {
          Sid       = "PublicReadGetObject",
          Effect    = "Allow",
          Principal = "*",
          Action = [
            "s3:GetObject"
          ],
          Resource = "${aws_s3_bucket.bakery_bucket.arn}/baked/*"
        }
      ]
  })
}

resource "aws_s3_bucket_policy" "site_bucket_policy" {
  bucket = aws_s3_bucket.site_bucket.id

  policy = jsonencode(
    {
      Version = "2012-10-17",
      Statement = [
        {
          Sid       = "PublicReadGetObject",
          Effect    = "Allow",
          Principal = "*",
          Action = [
            "s3:GetObject"
          ],
          Resource = "${aws_s3_bucket.site_bucket.arn}/*"
        }
      ]
  })
}



