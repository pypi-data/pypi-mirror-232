'''
# fastly-services-activeversion

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `Fastly::Services::ActiveVersion` v1.6.0.

## Description

Manage a Fastly service active version.

## References

* [Documentation](https://github.com/aws-ia/cloudformation-fastly-resource-providers)
* [Source](https://github.com/aws-ia/cloudformation-fastly-resource-providers.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name Fastly::Services::ActiveVersion \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/Fastly-Services-ActiveVersion \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `Fastly::Services::ActiveVersion`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Ffastly-services-activeversion+v1.6.0).
* Issues related to `Fastly::Services::ActiveVersion` should be reported to the [publisher](https://github.com/aws-ia/cloudformation-fastly-resource-providers).

## License

Distributed under the Apache-2.0 License.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import constructs as _constructs_77d1e7e8


class CfnActiveVersion(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/fastly-services-activeversion.CfnActiveVersion",
):
    '''A CloudFormation ``Fastly::Services::ActiveVersion``.

    :cloudformationResource: Fastly::Services::ActiveVersion
    :link: https://github.com/aws-ia/cloudformation-fastly-resource-providers.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        service_id: builtins.str,
        version_number: jsii.Number,
    ) -> None:
        '''Create a new ``Fastly::Services::ActiveVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param service_id: Alphanumeric string identifying the service. Read-only.
        :param version_number: The number of the version to be activated.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66c8f11b34ffed02f16859299829f0baa414548fa47cfea589e7371c814f1a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnActiveVersionProps(
            service_id=service_id, version_number=version_number
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnActiveVersionProps":
        '''Resource props.'''
        return typing.cast("CfnActiveVersionProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/fastly-services-activeversion.CfnActiveVersionProps",
    jsii_struct_bases=[],
    name_mapping={"service_id": "serviceId", "version_number": "versionNumber"},
)
class CfnActiveVersionProps:
    def __init__(
        self,
        *,
        service_id: builtins.str,
        version_number: jsii.Number,
    ) -> None:
        '''Manage a Fastly service active version.

        :param service_id: Alphanumeric string identifying the service. Read-only.
        :param version_number: The number of the version to be activated.

        :schema: CfnActiveVersionProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60491c981d7f49c6f0b27885e767f880321de2a6726de669abb1003beb2caf8)
            check_type(argname="argument service_id", value=service_id, expected_type=type_hints["service_id"])
            check_type(argname="argument version_number", value=version_number, expected_type=type_hints["version_number"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service_id": service_id,
            "version_number": version_number,
        }

    @builtins.property
    def service_id(self) -> builtins.str:
        '''Alphanumeric string identifying the service.

        Read-only.

        :schema: CfnActiveVersionProps#ServiceId
        '''
        result = self._values.get("service_id")
        assert result is not None, "Required property 'service_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version_number(self) -> jsii.Number:
        '''The number of the version to be activated.

        :schema: CfnActiveVersionProps#VersionNumber
        '''
        result = self._values.get("version_number")
        assert result is not None, "Required property 'version_number' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnActiveVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnActiveVersion",
    "CfnActiveVersionProps",
]

publication.publish()

def _typecheckingstub__e66c8f11b34ffed02f16859299829f0baa414548fa47cfea589e7371c814f1a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    service_id: builtins.str,
    version_number: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60491c981d7f49c6f0b27885e767f880321de2a6726de669abb1003beb2caf8(
    *,
    service_id: builtins.str,
    version_number: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass
