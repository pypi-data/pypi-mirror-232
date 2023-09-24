'''
[![NPM version](https://badge.fury.io/js/cdk-aws-iotfleetwise.svg)](https://badge.fury.io/js/cdk-aws-iotfleetwise)
[![PyPI version](https://badge.fury.io/py/cdk-aws-iotfleetwise.svg)](https://badge.fury.io/py/cdk-aws-iotfleetwise)
[![release](https://github.com/aws-samples/cdk-aws-iotfleetwise/actions/workflows/release.yml/badge.svg)](https://github.com/aws-samples/cdk-aws-iotfleetwise/actions/workflows/release.yml)

# cdk-aws-iotfleetwise

L2 CDK construct to provision AWS IoT Fleetwise

# Install

### Typescript

```sh
npm install cdk-aws-iotfleetwise
```

[API Reference](doc/api-typescript.md)

#### Python

```sh
pip install cdk-aws-iotfleetwise
```

[API Reference](doc/api-python.md)

# Sample

```python
import { SignalCatalog,
         VehicleModel,
         Vehicle,
         Campaign,
         CanVehicleInterface,
         CanVehicleSignal,
         SignalCatalogBranch,
         TimeBasedCollectionScheme
         } from 'cdk-aws-iotfleetwise';

const signalCatalog = new SignalCatalog(stack, 'SignalCatalog', {
  database,
  table,
  role,
  nodes: [
    new SignalCatalogBranch('Vehicle'),
    new SignalCatalogSensor('Vehicle.EngineTorque', 'DOUBLE'),
  ],
});

const model_a = new VehicleModel(stack, 'ModelA', {
  signalCatalog,
  name: 'modelA',
  description: 'Model A vehicle',
  networkInterfaces: [new CanVehicleInterface('1', 'vcan0')],
  signals: [
    new CanVehicleSignal('Vehicle.EngineTorque', '1',
      401, // messageId
      1.0, // factor
      true, // isBigEndian
      false, // isSigned
      8, // lenght
      0.0, // offset
      9), // startBit
  ],
});

const vin100 = new Vehicle(stack, 'vin100', {
  vehicleName: 'vin100',
  vehicleModel: model_a,
  createIotThing: true
});

new Campaign(stack, 'Campaign', {
  name: 'TimeBasedCampaign',
  target: vin100,
  collectionScheme: new TimeBasedCollectionScheme(cdk.Duration.seconds(10)),
  signals: [
    new CampaignSignal('Vehicle.EngineTorque'),
  ],
});
```

## Getting started

To deploy a simple end-to-end example you can use the following commands

```sh
yarn install
projen && projen compile
npx cdk -a lib/integ.full.js deploy -c key_name=mykey
```

Where `mykey` is an existing keypair name present in your account.
The deploy takes about 15 mins mostly due to compilation of the IoT FleetWise agent in the
EC2 instance that simulate the vehicle. Once deploy is finshed, data will start to show up in your Timestream table.

## TODO

Warning: this construct should be considered at alpha stage and is not feature complete.

* Implement updates for all the custom resources
* Conditional campaigns

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more
information.

## License

This code is licensed under the MIT-0 License. See the LICENSE file.
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

import aws_cdk
import constructs


class Campaign(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.Campaign",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        collection_scheme: "CollectionScheme",
        data_destination_configs: typing.Sequence["DataDestinationConfig"],
        name: builtins.str,
        signals: typing.Sequence["CampaignSignal"],
        target: "Vehicle",
        auto_approve: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param collection_scheme: 
        :param data_destination_configs: 
        :param name: 
        :param signals: 
        :param target: 
        :param auto_approve: 
        '''
        if __debug__:
            def stub(
                scope: constructs.Construct,
                id: builtins.str,
                *,
                collection_scheme: "CollectionScheme",
                data_destination_configs: typing.Sequence["DataDestinationConfig"],
                name: builtins.str,
                signals: typing.Sequence["CampaignSignal"],
                target: "Vehicle",
                auto_approve: typing.Optional[builtins.bool] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CampaignProps(
            collection_scheme=collection_scheme,
            data_destination_configs=data_destination_configs,
            name=name,
            signals=signals,
            target=target,
            auto_approve=auto_approve,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> "Vehicle":
        return typing.cast("Vehicle", jsii.get(self, "target"))


@jsii.data_type(
    jsii_type="cdk-aws-iotfleetwise.CampaignProps",
    jsii_struct_bases=[],
    name_mapping={
        "collection_scheme": "collectionScheme",
        "data_destination_configs": "dataDestinationConfigs",
        "name": "name",
        "signals": "signals",
        "target": "target",
        "auto_approve": "autoApprove",
    },
)
class CampaignProps:
    def __init__(
        self,
        *,
        collection_scheme: "CollectionScheme",
        data_destination_configs: typing.Sequence["DataDestinationConfig"],
        name: builtins.str,
        signals: typing.Sequence["CampaignSignal"],
        target: "Vehicle",
        auto_approve: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param collection_scheme: 
        :param data_destination_configs: 
        :param name: 
        :param signals: 
        :param target: 
        :param auto_approve: 
        '''
        if __debug__:
            def stub(
                *,
                collection_scheme: "CollectionScheme",
                data_destination_configs: typing.Sequence["DataDestinationConfig"],
                name: builtins.str,
                signals: typing.Sequence["CampaignSignal"],
                target: "Vehicle",
                auto_approve: typing.Optional[builtins.bool] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument collection_scheme", value=collection_scheme, expected_type=type_hints["collection_scheme"])
            check_type(argname="argument data_destination_configs", value=data_destination_configs, expected_type=type_hints["data_destination_configs"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument signals", value=signals, expected_type=type_hints["signals"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument auto_approve", value=auto_approve, expected_type=type_hints["auto_approve"])
        self._values: typing.Dict[str, typing.Any] = {
            "collection_scheme": collection_scheme,
            "data_destination_configs": data_destination_configs,
            "name": name,
            "signals": signals,
            "target": target,
        }
        if auto_approve is not None:
            self._values["auto_approve"] = auto_approve

    @builtins.property
    def collection_scheme(self) -> "CollectionScheme":
        result = self._values.get("collection_scheme")
        assert result is not None, "Required property 'collection_scheme' is missing"
        return typing.cast("CollectionScheme", result)

    @builtins.property
    def data_destination_configs(self) -> typing.List["DataDestinationConfig"]:
        result = self._values.get("data_destination_configs")
        assert result is not None, "Required property 'data_destination_configs' is missing"
        return typing.cast(typing.List["DataDestinationConfig"], result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def signals(self) -> typing.List["CampaignSignal"]:
        result = self._values.get("signals")
        assert result is not None, "Required property 'signals' is missing"
        return typing.cast(typing.List["CampaignSignal"], result)

    @builtins.property
    def target(self) -> "Vehicle":
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast("Vehicle", result)

    @builtins.property
    def auto_approve(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("auto_approve")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CampaignProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CampaignSignal(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.CampaignSignal",
):
    def __init__(
        self,
        name: builtins.str,
        max_sample_count: typing.Optional[jsii.Number] = None,
        minimum_sampling_interval: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param name: -
        :param max_sample_count: -
        :param minimum_sampling_interval: -
        '''
        if __debug__:
            def stub(
                name: builtins.str,
                max_sample_count: typing.Optional[jsii.Number] = None,
                minimum_sampling_interval: typing.Optional[aws_cdk.Duration] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument max_sample_count", value=max_sample_count, expected_type=type_hints["max_sample_count"])
            check_type(argname="argument minimum_sampling_interval", value=minimum_sampling_interval, expected_type=type_hints["minimum_sampling_interval"])
        jsii.create(self.__class__, self, [name, max_sample_count, minimum_sampling_interval])

    @jsii.member(jsii_name="toObject")
    def to_object(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toObject", []))


class CollectionScheme(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.CollectionScheme",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="toObject")
    def to_object(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toObject", []))

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def _scheme(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "scheme"))

    @_scheme.setter
    def _scheme(self, value: typing.Mapping[typing.Any, typing.Any]) -> None:
        if __debug__:
            def stub(value: typing.Mapping[typing.Any, typing.Any]) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value)


class DataDestinationConfig(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.DataDestinationConfig",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="toObject")
    def to_object(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toObject", []))

    @builtins.property
    @jsii.member(jsii_name="destinationConfig")
    def _destination_config(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "destinationConfig"))

    @_destination_config.setter
    def _destination_config(
        self,
        value: typing.Mapping[typing.Any, typing.Any],
    ) -> None:
        if __debug__:
            def stub(value: typing.Mapping[typing.Any, typing.Any]) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationConfig", value)


class Fleet(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.Fleet",
):
    '''The fleet of vehicles.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        fleet_id: builtins.str,
        signal_catalog: "SignalCatalog",
        description: typing.Optional[builtins.str] = None,
        vehicles: typing.Optional[typing.Sequence["Vehicle"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param fleet_id: 
        :param signal_catalog: 
        :param description: 
        :param vehicles: 
        '''
        if __debug__:
            def stub(
                scope: constructs.Construct,
                id: builtins.str,
                *,
                fleet_id: builtins.str,
                signal_catalog: "SignalCatalog",
                description: typing.Optional[builtins.str] = None,
                vehicles: typing.Optional[typing.Sequence["Vehicle"]] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FleetProps(
            fleet_id=fleet_id,
            signal_catalog=signal_catalog,
            description=description,
            vehicles=vehicles,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="fleetId")
    def fleet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fleetId"))

    @builtins.property
    @jsii.member(jsii_name="signalCatalog")
    def signal_catalog(self) -> "SignalCatalog":
        return typing.cast("SignalCatalog", jsii.get(self, "signalCatalog"))

    @builtins.property
    @jsii.member(jsii_name="vehicles")
    def vehicles(self) -> typing.Optional[typing.List["Vehicle"]]:
        return typing.cast(typing.Optional[typing.List["Vehicle"]], jsii.get(self, "vehicles"))


@jsii.data_type(
    jsii_type="cdk-aws-iotfleetwise.FleetProps",
    jsii_struct_bases=[],
    name_mapping={
        "fleet_id": "fleetId",
        "signal_catalog": "signalCatalog",
        "description": "description",
        "vehicles": "vehicles",
    },
)
class FleetProps:
    def __init__(
        self,
        *,
        fleet_id: builtins.str,
        signal_catalog: "SignalCatalog",
        description: typing.Optional[builtins.str] = None,
        vehicles: typing.Optional[typing.Sequence["Vehicle"]] = None,
    ) -> None:
        '''Interface.

        :param fleet_id: 
        :param signal_catalog: 
        :param description: 
        :param vehicles: 
        '''
        if __debug__:
            def stub(
                *,
                fleet_id: builtins.str,
                signal_catalog: "SignalCatalog",
                description: typing.Optional[builtins.str] = None,
                vehicles: typing.Optional[typing.Sequence["Vehicle"]] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument fleet_id", value=fleet_id, expected_type=type_hints["fleet_id"])
            check_type(argname="argument signal_catalog", value=signal_catalog, expected_type=type_hints["signal_catalog"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument vehicles", value=vehicles, expected_type=type_hints["vehicles"])
        self._values: typing.Dict[str, typing.Any] = {
            "fleet_id": fleet_id,
            "signal_catalog": signal_catalog,
        }
        if description is not None:
            self._values["description"] = description
        if vehicles is not None:
            self._values["vehicles"] = vehicles

    @builtins.property
    def fleet_id(self) -> builtins.str:
        result = self._values.get("fleet_id")
        assert result is not None, "Required property 'fleet_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def signal_catalog(self) -> "SignalCatalog":
        result = self._values.get("signal_catalog")
        assert result is not None, "Required property 'signal_catalog' is missing"
        return typing.cast("SignalCatalog", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vehicles(self) -> typing.Optional[typing.List["Vehicle"]]:
        result = self._values.get("vehicles")
        return typing.cast(typing.Optional[typing.List["Vehicle"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FleetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NetworkFileDefinition(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.NetworkFileDefinition",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="toObject")
    def to_object(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toObject", []))

    @builtins.property
    @jsii.member(jsii_name="definition")
    def _definition(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "definition"))

    @_definition.setter
    def _definition(self, value: typing.Mapping[typing.Any, typing.Any]) -> None:
        if __debug__:
            def stub(value: typing.Mapping[typing.Any, typing.Any]) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definition", value)


class S3ConfigProperty(
    DataDestinationConfig,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.S3ConfigProperty",
):
    def __init__(
        self,
        bucket_arn: builtins.str,
        data_format: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        storage_compression_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: -
        :param data_format: -
        :param prefix: -
        :param storage_compression_format: -
        '''
        if __debug__:
            def stub(
                bucket_arn: builtins.str,
                data_format: typing.Optional[builtins.str] = None,
                prefix: typing.Optional[builtins.str] = None,
                storage_compression_format: typing.Optional[builtins.str] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument bucket_arn", value=bucket_arn, expected_type=type_hints["bucket_arn"])
            check_type(argname="argument data_format", value=data_format, expected_type=type_hints["data_format"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument storage_compression_format", value=storage_compression_format, expected_type=type_hints["storage_compression_format"])
        jsii.create(self.__class__, self, [bucket_arn, data_format, prefix, storage_compression_format])


class SignalCatalog(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.SignalCatalog",
):
    '''The Signal Catalog represents the list of all signals that you want to collect from all the vehicles.

    The AWS IoT Fleetwise preview can only support a single Signal Catalog per account.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        nodes: typing.Sequence["SignalCatalogNode"],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param nodes: 
        :param description: 
        :param name: 
        '''
        if __debug__:
            def stub(
                scope: constructs.Construct,
                id: builtins.str,
                *,
                nodes: typing.Sequence["SignalCatalogNode"],
                description: typing.Optional[builtins.str] = None,
                name: typing.Optional[builtins.str] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SignalCatalogProps(nodes=nodes, description=description, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the signal catalog.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))


class SignalCatalogNode(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.SignalCatalogNode",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="toObject")
    def to_object(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toObject", []))

    @builtins.property
    @jsii.member(jsii_name="node")
    def _node(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "node"))

    @_node.setter
    def _node(self, value: typing.Mapping[typing.Any, typing.Any]) -> None:
        if __debug__:
            def stub(value: typing.Mapping[typing.Any, typing.Any]) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "node", value)


@jsii.data_type(
    jsii_type="cdk-aws-iotfleetwise.SignalCatalogProps",
    jsii_struct_bases=[],
    name_mapping={"nodes": "nodes", "description": "description", "name": "name"},
)
class SignalCatalogProps:
    def __init__(
        self,
        *,
        nodes: typing.Sequence[SignalCatalogNode],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param nodes: 
        :param description: 
        :param name: 
        '''
        if __debug__:
            def stub(
                *,
                nodes: typing.Sequence[SignalCatalogNode],
                description: typing.Optional[builtins.str] = None,
                name: typing.Optional[builtins.str] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument nodes", value=nodes, expected_type=type_hints["nodes"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[str, typing.Any] = {
            "nodes": nodes,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def nodes(self) -> typing.List[SignalCatalogNode]:
        result = self._values.get("nodes")
        assert result is not None, "Required property 'nodes' is missing"
        return typing.cast(typing.List[SignalCatalogNode], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SignalCatalogProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SignalCatalogSensor(
    SignalCatalogNode,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.SignalCatalogSensor",
):
    def __init__(
        self,
        fully_qualified_name: builtins.str,
        data_type: builtins.str,
        unit: typing.Optional[builtins.str] = None,
        min: typing.Optional[jsii.Number] = None,
        max: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fully_qualified_name: -
        :param data_type: -
        :param unit: -
        :param min: -
        :param max: -
        :param description: -
        '''
        if __debug__:
            def stub(
                fully_qualified_name: builtins.str,
                data_type: builtins.str,
                unit: typing.Optional[builtins.str] = None,
                min: typing.Optional[jsii.Number] = None,
                max: typing.Optional[jsii.Number] = None,
                description: typing.Optional[builtins.str] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument fully_qualified_name", value=fully_qualified_name, expected_type=type_hints["fully_qualified_name"])
            check_type(argname="argument data_type", value=data_type, expected_type=type_hints["data_type"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument min", value=min, expected_type=type_hints["min"])
            check_type(argname="argument max", value=max, expected_type=type_hints["max"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        jsii.create(self.__class__, self, [fully_qualified_name, data_type, unit, min, max, description])


class TimeBasedCollectionScheme(
    CollectionScheme,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.TimeBasedCollectionScheme",
):
    def __init__(self, period: aws_cdk.Duration) -> None:
        '''
        :param period: -
        '''
        if __debug__:
            def stub(period: aws_cdk.Duration) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
        jsii.create(self.__class__, self, [period])


class TimestreamConfigProperty(
    DataDestinationConfig,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.TimestreamConfigProperty",
):
    def __init__(
        self,
        execution_role_arn: builtins.str,
        timestream_table_arn: builtins.str,
    ) -> None:
        '''
        :param execution_role_arn: -
        :param timestream_table_arn: -
        '''
        if __debug__:
            def stub(
                execution_role_arn: builtins.str,
                timestream_table_arn: builtins.str,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument execution_role_arn", value=execution_role_arn, expected_type=type_hints["execution_role_arn"])
            check_type(argname="argument timestream_table_arn", value=timestream_table_arn, expected_type=type_hints["timestream_table_arn"])
        jsii.create(self.__class__, self, [execution_role_arn, timestream_table_arn])


class Vehicle(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.Vehicle",
):
    '''The vehicle of a specific type from which IoT FleetWise collect signals.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        create_iot_thing: builtins.bool,
        vehicle_model: "VehicleModel",
        vehicle_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param create_iot_thing: 
        :param vehicle_model: 
        :param vehicle_name: 
        '''
        if __debug__:
            def stub(
                scope: constructs.Construct,
                id: builtins.str,
                *,
                create_iot_thing: builtins.bool,
                vehicle_model: "VehicleModel",
                vehicle_name: builtins.str,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = VehicleProps(
            create_iot_thing=create_iot_thing,
            vehicle_model=vehicle_model,
            vehicle_name=vehicle_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="vehicleModel")
    def vehicle_model(self) -> "VehicleModel":
        return typing.cast("VehicleModel", jsii.get(self, "vehicleModel"))

    @builtins.property
    @jsii.member(jsii_name="vehicleName")
    def vehicle_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vehicleName"))

    @builtins.property
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateArn"))

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateId"))

    @builtins.property
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificatePem"))

    @builtins.property
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointAddress"))

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKey"))


class VehicleInterface(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.VehicleInterface",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="toObject")
    def to_object(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toObject", []))

    @builtins.property
    @jsii.member(jsii_name="intf")
    def _intf(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "intf"))

    @_intf.setter
    def _intf(self, value: typing.Mapping[typing.Any, typing.Any]) -> None:
        if __debug__:
            def stub(value: typing.Mapping[typing.Any, typing.Any]) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intf", value)


class VehicleModel(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.VehicleModel",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        network_interfaces: typing.Sequence[VehicleInterface],
        signal_catalog: SignalCatalog,
        description: typing.Optional[builtins.str] = None,
        network_file_definitions: typing.Optional[typing.Sequence[NetworkFileDefinition]] = None,
        signals: typing.Optional[typing.Sequence["VehicleSignal"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: 
        :param network_interfaces: 
        :param signal_catalog: 
        :param description: 
        :param network_file_definitions: 
        :param signals: 
        '''
        if __debug__:
            def stub(
                scope: constructs.Construct,
                id: builtins.str,
                *,
                name: builtins.str,
                network_interfaces: typing.Sequence[VehicleInterface],
                signal_catalog: SignalCatalog,
                description: typing.Optional[builtins.str] = None,
                network_file_definitions: typing.Optional[typing.Sequence[NetworkFileDefinition]] = None,
                signals: typing.Optional[typing.Sequence["VehicleSignal"]] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = VehicleModelProps(
            name=name,
            network_interfaces=network_interfaces,
            signal_catalog=signal_catalog,
            description=description,
            network_file_definitions=network_file_definitions,
            signals=signals,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="signalCatalog")
    def signal_catalog(self) -> SignalCatalog:
        return typing.cast(SignalCatalog, jsii.get(self, "signalCatalog"))


@jsii.data_type(
    jsii_type="cdk-aws-iotfleetwise.VehicleModelProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "network_interfaces": "networkInterfaces",
        "signal_catalog": "signalCatalog",
        "description": "description",
        "network_file_definitions": "networkFileDefinitions",
        "signals": "signals",
    },
)
class VehicleModelProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        network_interfaces: typing.Sequence[VehicleInterface],
        signal_catalog: SignalCatalog,
        description: typing.Optional[builtins.str] = None,
        network_file_definitions: typing.Optional[typing.Sequence[NetworkFileDefinition]] = None,
        signals: typing.Optional[typing.Sequence["VehicleSignal"]] = None,
    ) -> None:
        '''
        :param name: 
        :param network_interfaces: 
        :param signal_catalog: 
        :param description: 
        :param network_file_definitions: 
        :param signals: 
        '''
        if __debug__:
            def stub(
                *,
                name: builtins.str,
                network_interfaces: typing.Sequence[VehicleInterface],
                signal_catalog: SignalCatalog,
                description: typing.Optional[builtins.str] = None,
                network_file_definitions: typing.Optional[typing.Sequence[NetworkFileDefinition]] = None,
                signals: typing.Optional[typing.Sequence["VehicleSignal"]] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_interfaces", value=network_interfaces, expected_type=type_hints["network_interfaces"])
            check_type(argname="argument signal_catalog", value=signal_catalog, expected_type=type_hints["signal_catalog"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument network_file_definitions", value=network_file_definitions, expected_type=type_hints["network_file_definitions"])
            check_type(argname="argument signals", value=signals, expected_type=type_hints["signals"])
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "network_interfaces": network_interfaces,
            "signal_catalog": signal_catalog,
        }
        if description is not None:
            self._values["description"] = description
        if network_file_definitions is not None:
            self._values["network_file_definitions"] = network_file_definitions
        if signals is not None:
            self._values["signals"] = signals

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_interfaces(self) -> typing.List[VehicleInterface]:
        result = self._values.get("network_interfaces")
        assert result is not None, "Required property 'network_interfaces' is missing"
        return typing.cast(typing.List[VehicleInterface], result)

    @builtins.property
    def signal_catalog(self) -> SignalCatalog:
        result = self._values.get("signal_catalog")
        assert result is not None, "Required property 'signal_catalog' is missing"
        return typing.cast(SignalCatalog, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_file_definitions(
        self,
    ) -> typing.Optional[typing.List[NetworkFileDefinition]]:
        result = self._values.get("network_file_definitions")
        return typing.cast(typing.Optional[typing.List[NetworkFileDefinition]], result)

    @builtins.property
    def signals(self) -> typing.Optional[typing.List["VehicleSignal"]]:
        result = self._values.get("signals")
        return typing.cast(typing.Optional[typing.List["VehicleSignal"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VehicleModelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-aws-iotfleetwise.VehicleProps",
    jsii_struct_bases=[],
    name_mapping={
        "create_iot_thing": "createIotThing",
        "vehicle_model": "vehicleModel",
        "vehicle_name": "vehicleName",
    },
)
class VehicleProps:
    def __init__(
        self,
        *,
        create_iot_thing: builtins.bool,
        vehicle_model: VehicleModel,
        vehicle_name: builtins.str,
    ) -> None:
        '''Interface.

        :param create_iot_thing: 
        :param vehicle_model: 
        :param vehicle_name: 
        '''
        if __debug__:
            def stub(
                *,
                create_iot_thing: builtins.bool,
                vehicle_model: VehicleModel,
                vehicle_name: builtins.str,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument create_iot_thing", value=create_iot_thing, expected_type=type_hints["create_iot_thing"])
            check_type(argname="argument vehicle_model", value=vehicle_model, expected_type=type_hints["vehicle_model"])
            check_type(argname="argument vehicle_name", value=vehicle_name, expected_type=type_hints["vehicle_name"])
        self._values: typing.Dict[str, typing.Any] = {
            "create_iot_thing": create_iot_thing,
            "vehicle_model": vehicle_model,
            "vehicle_name": vehicle_name,
        }

    @builtins.property
    def create_iot_thing(self) -> builtins.bool:
        result = self._values.get("create_iot_thing")
        assert result is not None, "Required property 'create_iot_thing' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def vehicle_model(self) -> VehicleModel:
        result = self._values.get("vehicle_model")
        assert result is not None, "Required property 'vehicle_model' is missing"
        return typing.cast(VehicleModel, result)

    @builtins.property
    def vehicle_name(self) -> builtins.str:
        result = self._values.get("vehicle_name")
        assert result is not None, "Required property 'vehicle_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VehicleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VehicleSignal(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.VehicleSignal",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="toObject")
    def to_object(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toObject", []))

    @builtins.property
    @jsii.member(jsii_name="signal")
    def _signal(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "signal"))

    @_signal.setter
    def _signal(self, value: typing.Mapping[typing.Any, typing.Any]) -> None:
        if __debug__:
            def stub(value: typing.Mapping[typing.Any, typing.Any]) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signal", value)


class CanDefinition(
    NetworkFileDefinition,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.CanDefinition",
):
    def __init__(
        self,
        network_interface: builtins.str,
        signals_map: typing.Mapping[builtins.str, builtins.str],
        can_dbc_files: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param network_interface: -
        :param signals_map: -
        :param can_dbc_files: -
        '''
        if __debug__:
            def stub(
                network_interface: builtins.str,
                signals_map: typing.Mapping[builtins.str, builtins.str],
                can_dbc_files: typing.Sequence[builtins.str],
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
            check_type(argname="argument signals_map", value=signals_map, expected_type=type_hints["signals_map"])
            check_type(argname="argument can_dbc_files", value=can_dbc_files, expected_type=type_hints["can_dbc_files"])
        jsii.create(self.__class__, self, [network_interface, signals_map, can_dbc_files])


class CanVehicleInterface(
    VehicleInterface,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.CanVehicleInterface",
):
    def __init__(self, interface_id: builtins.str, name: builtins.str) -> None:
        '''
        :param interface_id: -
        :param name: -
        '''
        if __debug__:
            def stub(interface_id: builtins.str, name: builtins.str) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument interface_id", value=interface_id, expected_type=type_hints["interface_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        jsii.create(self.__class__, self, [interface_id, name])


class CanVehicleSignal(
    VehicleSignal,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.CanVehicleSignal",
):
    def __init__(
        self,
        fully_qualified_name: builtins.str,
        interface_id: builtins.str,
        message_id: jsii.Number,
        factor: jsii.Number,
        is_big_endian: builtins.bool,
        is_signed: builtins.bool,
        length: jsii.Number,
        offset: jsii.Number,
        start_bit: jsii.Number,
    ) -> None:
        '''
        :param fully_qualified_name: -
        :param interface_id: -
        :param message_id: -
        :param factor: -
        :param is_big_endian: -
        :param is_signed: -
        :param length: -
        :param offset: -
        :param start_bit: -
        '''
        if __debug__:
            def stub(
                fully_qualified_name: builtins.str,
                interface_id: builtins.str,
                message_id: jsii.Number,
                factor: jsii.Number,
                is_big_endian: builtins.bool,
                is_signed: builtins.bool,
                length: jsii.Number,
                offset: jsii.Number,
                start_bit: jsii.Number,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument fully_qualified_name", value=fully_qualified_name, expected_type=type_hints["fully_qualified_name"])
            check_type(argname="argument interface_id", value=interface_id, expected_type=type_hints["interface_id"])
            check_type(argname="argument message_id", value=message_id, expected_type=type_hints["message_id"])
            check_type(argname="argument factor", value=factor, expected_type=type_hints["factor"])
            check_type(argname="argument is_big_endian", value=is_big_endian, expected_type=type_hints["is_big_endian"])
            check_type(argname="argument is_signed", value=is_signed, expected_type=type_hints["is_signed"])
            check_type(argname="argument length", value=length, expected_type=type_hints["length"])
            check_type(argname="argument offset", value=offset, expected_type=type_hints["offset"])
            check_type(argname="argument start_bit", value=start_bit, expected_type=type_hints["start_bit"])
        jsii.create(self.__class__, self, [fully_qualified_name, interface_id, message_id, factor, is_big_endian, is_signed, length, offset, start_bit])


class SignalCatalogBranch(
    SignalCatalogNode,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aws-iotfleetwise.SignalCatalogBranch",
):
    def __init__(
        self,
        fully_qualified_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fully_qualified_name: -
        :param description: -
        '''
        if __debug__:
            def stub(
                fully_qualified_name: builtins.str,
                description: typing.Optional[builtins.str] = None,
            ) -> None:
                ...
            type_hints = typing.get_type_hints(stub)
            check_type(argname="argument fully_qualified_name", value=fully_qualified_name, expected_type=type_hints["fully_qualified_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        jsii.create(self.__class__, self, [fully_qualified_name, description])


__all__ = [
    "Campaign",
    "CampaignProps",
    "CampaignSignal",
    "CanDefinition",
    "CanVehicleInterface",
    "CanVehicleSignal",
    "CollectionScheme",
    "DataDestinationConfig",
    "Fleet",
    "FleetProps",
    "NetworkFileDefinition",
    "S3ConfigProperty",
    "SignalCatalog",
    "SignalCatalogBranch",
    "SignalCatalogNode",
    "SignalCatalogProps",
    "SignalCatalogSensor",
    "TimeBasedCollectionScheme",
    "TimestreamConfigProperty",
    "Vehicle",
    "VehicleInterface",
    "VehicleModel",
    "VehicleModelProps",
    "VehicleProps",
    "VehicleSignal",
]

publication.publish()
