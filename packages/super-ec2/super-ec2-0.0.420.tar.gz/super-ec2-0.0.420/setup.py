import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "super-ec2",
    "version": "0.0.420",
    "description": "A construct lib for AWS CDK EC2",
    "license": "Apache-2.0",
    "url": "https://github.com/cdk-constructs-zone/super-ec2.git",
    "long_description_content_type": "text/markdown",
    "author": "@cdk-constructs-zone",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdk-constructs-zone/super-ec2.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "super_ec2",
        "super_ec2._jsii"
    ],
    "package_data": {
        "super_ec2._jsii": [
            "super-ec2@0.0.420.jsii.tgz"
        ],
        "super_ec2": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk.aws-autoscaling-hooktargets>=1.171.0, <2.0.0",
        "aws-cdk.aws-autoscaling>=1.171.0, <2.0.0",
        "aws-cdk.aws-certificatemanager>=1.171.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.171.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2-targets>=1.171.0, <2.0.0",
        "aws-cdk.aws-elasticloadbalancingv2>=1.171.0, <2.0.0",
        "aws-cdk.aws-iam>=1.171.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.171.0, <2.0.0",
        "aws-cdk.aws-logs>=1.171.0, <2.0.0",
        "aws-cdk.aws-route53-targets>=1.171.0, <2.0.0",
        "aws-cdk.aws-route53>=1.171.0, <2.0.0",
        "aws-cdk.aws-s3-assets>=1.171.0, <2.0.0",
        "aws-cdk.aws-s3>=1.171.0, <2.0.0",
        "aws-cdk.aws-sns-subscriptions>=1.171.0, <2.0.0",
        "aws-cdk.aws-sns>=1.171.0, <2.0.0",
        "aws-cdk.core>=1.171.0, <2.0.0",
        "aws-cdk.custom-resources>=1.171.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.89.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
