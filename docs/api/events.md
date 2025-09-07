# AEC Suite Estimate Events 1.0.0 documentation

* Specification ID: `urn:aec-suite:estimate-events:1.0.0`
* License: [MIT](https://opensource.org/licenses/MIT)
* Default content type: [application/json](https://www.iana.org/assignments/media-types/application/json)
* Support: [LX Solutions Engineering](https://lxsolutions.com)
* Email support: [engineering@lxsolutions.com](mailto:engineering@lxsolutions.com)

Event-driven architecture for estimate lifecycle management in AEC Suite
##### Specification tags

| Name | Description | Documentation |
|---|---|---|
| estimates | Estimate lifecycle management events | - |
| aec | Architecture, Engineering, and Construction events | - |


## Table of Contents

* [Servers](#servers)
  * [nats](#nats-server)
* [Operations](#operations)
  * [PUB estimate.created](#pub-estimatecreated-operation)
  * [SUB estimate.created](#sub-estimatecreated-operation)
  * [PUB estimate.approved](#pub-estimateapproved-operation)
  * [SUB estimate.approved](#sub-estimateapproved-operation)
  * [PUB estimate.rejected](#pub-estimaterejected-operation)
  * [SUB estimate.rejected](#sub-estimaterejected-operation)

## Servers

### `nats` Server

* URL: `nats://localhost:4222`
* Protocol: `nats`

NATS server for event streaming


## Operations

### PUB `estimate.created` Operation

* Operation ID: `publishEstimateCreated`

Event published when a new estimate is created

#### Message Estimate Created Event `estimateCreated`

*Published when a new estimate is created*

* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| estimateId | string | Unique identifier for the estimate | - | format (`uuid`) | **required** |
| projectId | string | Identifier of the project this estimate belongs to | - | format (`uuid`) | **required** |
| orgId | string | Identifier of the organization | - | format (`uuid`) | **required** |
| totals | object | - | - | - | **required**, **additional properties are allowed** |
| totals.subtotal | number | Subtotal amount before tax | - | format (`float`) | **required** |
| totals.tax | number | Tax amount | - | format (`float`) | **required** |
| totals.total | number | Total amount including tax | - | format (`float`) | **required** |
| totals.currency | string | Currency code (ISO 4217) | default (`"USD"`) | - | - |
| totals.laborCost | number | Labor cost component | - | format (`float`) | - |
| totals.materialCost | number | Material cost component | - | format (`float`) | - |
| totals.equipmentCost | number | Equipment cost component | - | format (`float`) | - |
| createdAt | string | Timestamp when the estimate was created | - | format (`date-time`) | - |
| createdBy | string | User ID who created the estimate | - | format (`uuid`) | - |

> Examples of payload _(generated)_

```json
{
  "estimateId": "de5c069b-4ec4-4b77-b171-2dd0db6cdf52",
  "projectId": "5a8591dd-4039-49df-9202-96385ba3eff8",
  "orgId": "25b2c2d5-a7fc-47d0-89e4-8709a1560bfa",
  "totals": {
    "subtotal": 0.1,
    "tax": 0.1,
    "total": 0.1,
    "currency": "USD",
    "laborCost": 0.1,
    "materialCost": 0.1,
    "equipmentCost": 0.1
  },
  "createdAt": "2019-08-24T14:15:22Z",
  "createdBy": "25a02396-1048-48f9-bf93-102d2fb7895e"
}
```



### SUB `estimate.created` Operation

* Operation ID: `subscribeEstimateCreated`

Event published when a new estimate is created

#### Message Estimate Created Event `estimateCreated`

*Published when a new estimate is created*

* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| estimateId | string | Unique identifier for the estimate | - | format (`uuid`) | **required** |
| projectId | string | Identifier of the project this estimate belongs to | - | format (`uuid`) | **required** |
| orgId | string | Identifier of the organization | - | format (`uuid`) | **required** |
| totals | object | - | - | - | **required**, **additional properties are allowed** |
| totals.subtotal | number | Subtotal amount before tax | - | format (`float`) | **required** |
| totals.tax | number | Tax amount | - | format (`float`) | **required** |
| totals.total | number | Total amount including tax | - | format (`float`) | **required** |
| totals.currency | string | Currency code (ISO 4217) | default (`"USD"`) | - | - |
| totals.laborCost | number | Labor cost component | - | format (`float`) | - |
| totals.materialCost | number | Material cost component | - | format (`float`) | - |
| totals.equipmentCost | number | Equipment cost component | - | format (`float`) | - |
| createdAt | string | Timestamp when the estimate was created | - | format (`date-time`) | - |
| createdBy | string | User ID who created the estimate | - | format (`uuid`) | - |

> Examples of payload _(generated)_

```json
{
  "estimateId": "de5c069b-4ec4-4b77-b171-2dd0db6cdf52",
  "projectId": "5a8591dd-4039-49df-9202-96385ba3eff8",
  "orgId": "25b2c2d5-a7fc-47d0-89e4-8709a1560bfa",
  "totals": {
    "subtotal": 0.1,
    "tax": 0.1,
    "total": 0.1,
    "currency": "USD",
    "laborCost": 0.1,
    "materialCost": 0.1,
    "equipmentCost": 0.1
  },
  "createdAt": "2019-08-24T14:15:22Z",
  "createdBy": "25a02396-1048-48f9-bf93-102d2fb7895e"
}
```



### PUB `estimate.approved` Operation

* Operation ID: `publishEstimateApproved`

Event published when an estimate is approved

#### Message Estimate Approved Event `estimateApproved`

*Published when an estimate is approved*

* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| estimateId | string | Unique identifier for the estimate | - | format (`uuid`) | **required** |
| userId | string | User ID who approved the estimate | - | format (`uuid`) | **required** |
| timestamp | string | Timestamp when the estimate was approved | - | format (`date-time`) | **required** |
| comment | string | Optional comment for approval | - | - | - |
| approvedAmount | number | Final approved amount | - | format (`float`) | - |

> Examples of payload _(generated)_

```json
{
  "estimateId": "de5c069b-4ec4-4b77-b171-2dd0db6cdf52",
  "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
  "timestamp": "2019-08-24T14:15:22Z",
  "comment": "string",
  "approvedAmount": 0.1
}
```



### SUB `estimate.approved` Operation

* Operation ID: `subscribeEstimateApproved`

Event published when an estimate is approved

#### Message Estimate Approved Event `estimateApproved`

*Published when an estimate is approved*

* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| estimateId | string | Unique identifier for the estimate | - | format (`uuid`) | **required** |
| userId | string | User ID who approved the estimate | - | format (`uuid`) | **required** |
| timestamp | string | Timestamp when the estimate was approved | - | format (`date-time`) | **required** |
| comment | string | Optional comment for approval | - | - | - |
| approvedAmount | number | Final approved amount | - | format (`float`) | - |

> Examples of payload _(generated)_

```json
{
  "estimateId": "de5c069b-4ec4-4b77-b171-2dd0db6cdf52",
  "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
  "timestamp": "2019-08-24T14:15:22Z",
  "comment": "string",
  "approvedAmount": 0.1
}
```



### PUB `estimate.rejected` Operation

* Operation ID: `publishEstimateRejected`

Event published when an estimate is rejected

#### Message Estimate Rejected Event `estimateRejected`

*Published when an estimate is rejected*

* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| estimateId | string | Unique identifier for the estimate | - | format (`uuid`) | **required** |
| userId | string | User ID who rejected the estimate | - | format (`uuid`) | **required** |
| timestamp | string | Timestamp when the estimate was rejected | - | format (`date-time`) | **required** |
| comment | string | Reason for rejection | - | - | - |
| issues | array&lt;string&gt; | List of specific issues identified | - | - | - |
| issues (single item) | string | - | - | - | - |

> Examples of payload _(generated)_

```json
{
  "estimateId": "de5c069b-4ec4-4b77-b171-2dd0db6cdf52",
  "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
  "timestamp": "2019-08-24T14:15:22Z",
  "comment": "string",
  "issues": [
    "string"
  ]
}
```



### SUB `estimate.rejected` Operation

* Operation ID: `subscribeEstimateRejected`

Event published when an estimate is rejected

#### Message Estimate Rejected Event `estimateRejected`

*Published when an estimate is rejected*

* Content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| estimateId | string | Unique identifier for the estimate | - | format (`uuid`) | **required** |
| userId | string | User ID who rejected the estimate | - | format (`uuid`) | **required** |
| timestamp | string | Timestamp when the estimate was rejected | - | format (`date-time`) | **required** |
| comment | string | Reason for rejection | - | - | - |
| issues | array&lt;string&gt; | List of specific issues identified | - | - | - |
| issues (single item) | string | - | - | - | - |

> Examples of payload _(generated)_

```json
{
  "estimateId": "de5c069b-4ec4-4b77-b171-2dd0db6cdf52",
  "userId": "2c4a230c-5085-4924-a3e1-25fb4fc5965b",
  "timestamp": "2019-08-24T14:15:22Z",
  "comment": "string",
  "issues": [
    "string"
  ]
}
```



