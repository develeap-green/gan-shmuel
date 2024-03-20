# Gan Shmuel - Weight Microservice
> The Weight Microservice is responsible for the industrial weighing of trucks, facilitating the payment process to providers based on the cargo's net weight.
> The application, WeightApp, maintains a record of all weights, ensuring payments are calculated accurately.
> Reminder: `Bruto = Neto (fruit) + Tara (truck) + sum(Tara (containers))`

## API Routes

### POST /weight
>Records the weight of trucks or standalone containers and returns a JSON object with a unique weight measurement.

#### Parameters:
| Name  	|   Value	      |  Description 	|
|---	    |---	          |---	|
| direction	|`in` / `out` / `none`|Specifies the weighing direction; options are `in`, `out`, or `none` (for standalone containers).|
| truck	    |`str` / `na`     |The license plate of the truck if applicable, otherwise `na`.|
| containers|`list[str]`	  |A comma-separated list of container IDs involved in the weighing.|
| weight	|`int`   	      |The weight measurement as an integer.|
| unit	    | `kg` / `lbs`  	  |The unit of weight, either `kg` or `lbs`. Precision is approximately 5kg, so decimals are not considered.|
| force	    |`bool`  	      |A boolean flag (true/False). When set to true, it allows overwriting the previous weight of the same truck.|
| produce	|`str` / `na`     |The ID of the produce (e.g., "orange", "tomato"), or `na` if not applicable.|

#### Behavior:
* Recording an `in` or `none` direction generates a new `session_id`.
* Recording an `out` direction returns the `session_id` of the previous `in` for the truck.
* Submitting `in` after `in` or `out` after `out` without `force=true` will result in an error.
* Submitting `out` without a preceding `in` or `none` after `in` will also result in an error.

##### Success Response:
```json
{
  "id": "1205",
  "truck": "T-17744",
  "bruto": 3350,

  // ONLY IF DIRECTION "out" ADD
  "truckTara": 150,
  "neto": 2000
}
```

### POST /batch-weight
> Uploads a list of tara weights from a specified file located in the "/in" folder. This is typically used for registering a batch of new containers.

#### Parameters:

| Name  	|   Type	|   Description	|
|---	    |---	    |---	        |
|   file	    |  `csv` / `json` 	    |   The name of the file containing the tara weights	        |


##### Accepted File Formats:
`csv`:
> ("id", "kg")
> OR 
> ("id", "lbs")

`json`:
```json
[
    {
        "id": "container_id",
        "weight": weight,
        "unit": "kg/lbs"
    }, 
    // .....
]
``` 

### GET /unknown
> Returns a list of all containers that have an unknown weight.

##### Response Example:

```json

["id1", "id2", ...]
```
### GET /weight?from=t1&to=t2&filter=f
> Retrieves a list of weight records within a specified time range and filter.

#### Parameters:
|  Name   | Type  	| Description  	|
|---	  |---	|---	|
| from    |  `str` 	|   Start date-time stamp formatted as `yyyymmddhhmmss`. Defaults to the start of the current day.	|
| to	  |   `str` 	|  End date-time stamp formatted as `yyyymmddhhmmss`. Defaults to the current time. 	|
| filter  |  `[str]` 	|   A comma-separated list of directions to filter by (`in`, `out`, `none`). Defaults to all directions.	|


##### Response Example:

```json

[
  {
    "id": "id",
    "direction": "in/out/none",
    "bruto": "total_weight",
    "neto": "net_weight or na (if some container taras are unknown)",
    "produce": "produce_id",
    "containers": ["id1", "id2", ...]
  },
  // ...
]
```
### GET /item/:id?from=t1&to=t2
> Returns details for a specific item (truck or container) within a specified time range.

#### Parameters:
|  Name   |  Type 	| Description  	|
|---	  |---	|---	|
| id    |  `str` 	| The ID of the item (truck or container).	|
| from	  |   `datetime` 	| Start date-time stamp, defaulting to the first of the current month at 000000. |
| to  |  `datetime` 	|    End date-time stamp, defaulting to the current time.	|


##### Response Example:

```json
{
  "id": "C-65816",
  "tara": 3500,
  "sessions": ["session_id1", "session_id2", ...]
}
```

#### GET /session/:id
> Retrieves details for a specific weighing session.

### Parameters:
|   Name	|  Type 	|   Description	                    |
|---	    |---	    |---	                            |
|   id	    |   `str`	|  The ID of the weighing session. 	| 

##### Response Example:

```json
{
  "id": "session_id",
  "truck": "truck_id or na",
  "bruto": "total_weight",
  "truckTara": "truck_tara_weight (only for out direction)",
  "neto": "net_weight or na (if some container taras are unknown)"
}
```
#### GET /health
> Checks the health of the system.

#### Behavior:

* Returns "OK" with a 200 OK status by default.
* If the system depends on external resources (e.g., a database) and they are not available, it returns "Failure" with a 500 Internal Server Error.



