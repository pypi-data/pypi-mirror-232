'''
# fastly-services-version

> AWS CDK [L1 construct](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html) and data structures for the [AWS CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html) type `Fastly::Services::Version` v1.6.0.

## Description

Manage a Fastly service version.

## References

* [Documentation](https://github.com/aws-ia/cloudformation-fastly-resource-providers)
* [Source](https://github.com/aws-ia/cloudformation-fastly-resource-providers.git)

## Usage

In order to use this library, you will need to activate this AWS CloudFormation Registry type in your account. You can do this via the AWS Management Console or using the [AWS CLI](https://aws.amazon.com/cli/) using the following command:

```sh
aws cloudformation activate-type \
  --type-name Fastly::Services::Version \
  --publisher-id c830e97710da0c9954d80ba8df021e5439e7134b \
  --type RESOURCE \
  --execution-role-arn ROLE-ARN
```

Alternatively:

```sh
aws cloudformation activate-type \
  --public-type-arn arn:aws:cloudformation:us-east-1::type/resource/c830e97710da0c9954d80ba8df021e5439e7134b/Fastly-Services-Version \
  --execution-role-arn ROLE-ARN
```

You can find more information about activating this type in the [AWS CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry-public.html).

## Feedback

This library is auto-generated and published to all supported programming languages by the [cdklabs/cdk-cloudformation](https://github.com/cdklabs/cdk-cloudformation) project based on the API schema published for `Fastly::Services::Version`.

* Issues related to this generated library should be [reported here](https://github.com/cdklabs/cdk-cloudformation/issues/new?title=Issue+with+%40cdk-cloudformation%2Ffastly-services-version+v1.6.0).
* Issues related to `Fastly::Services::Version` should be reported to the [publisher](https://github.com/aws-ia/cloudformation-fastly-resource-providers).

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


class CfnVersion(
    _aws_cdk_ceddda9d.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-cloudformation/fastly-services-version.CfnVersion",
):
    '''A CloudFormation ``Fastly::Services::Version``.

    :cloudformationResource: Fastly::Services::Version
    :link: https://github.com/aws-ia/cloudformation-fastly-resource-providers.git
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        service_id: builtins.str,
        created_at: typing.Optional[datetime.datetime] = None,
        deleted_at: typing.Optional[datetime.datetime] = None,
        updated_at: typing.Optional[datetime.datetime] = None,
    ) -> None:
        '''Create a new ``Fastly::Services::Version``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param service_id: Alphanumeric string identifying the service. Read-only.
        :param created_at: 
        :param deleted_at: 
        :param updated_at: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__addebe63b39f2e10f4e4fbdb79eb53275014a6dd0c7dcba610012c282c3827c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnVersionProps(
            service_id=service_id,
            created_at=created_at,
            deleted_at=deleted_at,
            updated_at=updated_at,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrVersionNumber")
    def attr_version_number(self) -> jsii.Number:
        '''Attribute ``Fastly::Services::Version.VersionNumber``.

        :link: https://github.com/aws-ia/cloudformation-fastly-resource-providers.git
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrVersionNumber"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "CfnVersionProps":
        '''Resource props.'''
        return typing.cast("CfnVersionProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@cdk-cloudformation/fastly-services-version.CfnVersionProps",
    jsii_struct_bases=[],
    name_mapping={
        "service_id": "serviceId",
        "created_at": "createdAt",
        "deleted_at": "deletedAt",
        "updated_at": "updatedAt",
    },
)
class CfnVersionProps:
    def __init__(
        self,
        *,
        service_id: builtins.str,
        created_at: typing.Optional[datetime.datetime] = None,
        deleted_at: typing.Optional[datetime.datetime] = None,
        updated_at: typing.Optional[datetime.datetime] = None,
    ) -> None:
        '''Manage a Fastly service version.

        :param service_id: Alphanumeric string identifying the service. Read-only.
        :param created_at: 
        :param deleted_at: 
        :param updated_at: 

        :schema: CfnVersionProps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3075d35034098bc8d973e467c332d4f2ba8b2cd02b781c0919b76d0d7310d17)
            check_type(argname="argument service_id", value=service_id, expected_type=type_hints["service_id"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument deleted_at", value=deleted_at, expected_type=type_hints["deleted_at"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service_id": service_id,
        }
        if created_at is not None:
            self._values["created_at"] = created_at
        if deleted_at is not None:
            self._values["deleted_at"] = deleted_at
        if updated_at is not None:
            self._values["updated_at"] = updated_at

    @builtins.property
    def service_id(self) -> builtins.str:
        '''Alphanumeric string identifying the service.

        Read-only.

        :schema: CfnVersionProps#ServiceId
        '''
        result = self._values.get("service_id")
        assert result is not None, "Required property 'service_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_at(self) -> typing.Optional[datetime.datetime]:
        '''
        :schema: CfnVersionProps#CreatedAt
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[datetime.datetime], result)

    @builtins.property
    def deleted_at(self) -> typing.Optional[datetime.datetime]:
        '''
        :schema: CfnVersionProps#DeletedAt
        '''
        result = self._values.get("deleted_at")
        return typing.cast(typing.Optional[datetime.datetime], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[datetime.datetime]:
        '''
        :schema: CfnVersionProps#UpdatedAt
        '''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[datetime.datetime], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnVersion",
    "CfnVersionProps",
]

publication.publish()

def _typecheckingstub__addebe63b39f2e10f4e4fbdb79eb53275014a6dd0c7dcba610012c282c3827c3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    service_id: builtins.str,
    created_at: typing.Optional[datetime.datetime] = None,
    deleted_at: typing.Optional[datetime.datetime] = None,
    updated_at: typing.Optional[datetime.datetime] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3075d35034098bc8d973e467c332d4f2ba8b2cd02b781c0919b76d0d7310d17(
    *,
    service_id: builtins.str,
    created_at: typing.Optional[datetime.datetime] = None,
    deleted_at: typing.Optional[datetime.datetime] = None,
    updated_at: typing.Optional[datetime.datetime] = None,
) -> None:
    """Type checking stubs"""
    pass
