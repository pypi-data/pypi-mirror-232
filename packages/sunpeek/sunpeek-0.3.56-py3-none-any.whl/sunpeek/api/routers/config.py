from fastapi import APIRouter, Depends
from typing import List, Union
import enum
from sqlalchemy.orm import Session

import sunpeek.components as cmp
from sunpeek.api.dependencies import session, crud
import sunpeek.serializable_models as smodels
from sunpeek.common.errors import ConfigurationError
import sunpeek.components.sensor_types as st
from sunpeek.api.routers.helper import update_obj, update_plant

config_router = APIRouter(
    prefix="/config",
    tags=["config"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@config_router.get("/ping")
def ping_harvestIT_old():
    """old version for backward compatibility"""
    return "success"


@config_router.get("/ping_backend")
def ping_harvestIT():
    return "success"


@config_router.get("/ping_database")
def ping_database(sess: Session = Depends(session)):
    sess.execute('SELECT 1')
    return True


# @config_router.post("/sensors", response_model=Union[smodels.Sensor, List[smodels.Sensor]], tags=["sensors"],
#                     responses= {409: {"description": "Conflict, most likely because the plant name or name of a child object already exists",
#                     "model": smodels.Error}}))
# def sensors(id: int = None, raw_name: str=None, plant_id: int = None, plant_name: str = None,
#             sess: Session = Depends(session), crud = Depends(crud)):
#     sensors = crud.get_sensors(sess, id, raw_name, plant_id, plant_name)
#     return sensors


@config_router.get("/sensor_types",
                   response_model=Union[smodels.SensorTypeValidator, List[smodels.SensorTypeValidator]],
                   tags=["sensors"], summary="Get a list of sensor types, or select by id or name and plant")
def sensor_types(name: str = None):
    if name is not None:
        return getattr(st, name)
    return st.all_sensor_types


@config_router.get("/fluid_definitions",
                   response_model=Union[List[smodels.FluidDefintion], smodels.FluidDefintion],
                   tags=["fluids"], summary="Get a single list of fluid_definitions, or select by id or name and plant")
def fluids(id: int = None, 
           name: str = None, 
           plant_id: int = None, 
           plant_name: str = None,
           sess: Session = Depends(session), 
           crd=Depends(crud)):
    
    return crd.get_components(sess, cmp.FluidDefinition, id, name, plant_id, plant_name)


@config_router.get("/fluid_definitions/{id}", response_model=smodels.FluidDefintion, tags=["fluids"],
                   summary="Get a single fluid definition by id")
def fluids(id: int = None, 
           name: str = None, 
           plant_id: int = None, 
           plant_name: str = None,
           sess: Session = Depends(session), 
           crd=Depends(crud)):
    
    return crd.get_components(sess, cmp.FluidDefinition, id, name, plant_id, plant_name)


@config_router.get("/collectors", response_model=Union[List[smodels.CollectorType], smodels.CollectorType],
                   tags=["collectors"], summary="Get a list of collector types, or select by id or name, or filter by "
                                                "types used in a certain plant")
def collector_types(id: int = None, 
                    name: str = None, 
                    plant_id: int = None, 
                    plant_name: str = None,
                    sess: Session = Depends(session), 
                    crd=Depends(crud)):
    if plant_id is not None or plant_name is not None:
        plant = crd.get_plants(sess, plant_id, plant_name)
        return [array.collector_type for array in plant.arrays]

    return crd.get_components(sess, cmp.CollectorType, id, name)


@config_router.post("/collectors/new",
                    response_model=Union[smodels.CollectorType, List[smodels.CollectorType]],
                    tags=["collectors"],
                    status_code=201,
                    summary="Create a new collector type or types")
def create_collector_type(collector: Union[
    smodels.CollectorTypeSST, smodels.CollectorTypeQDT, List[smodels.CollectorTypeSST], List[smodels.CollectorTypeQDT]],
                          sess: Session = Depends(session),
                          crd=Depends(crud)):
    if not isinstance(collector, list):
        collectors = [collector]
    else:
        collectors = collector

    for i, collector in enumerate(collectors):
        type_dict = collector.dict(exclude_unset=True)
        test_type = type_dict.pop('test_type')
        if test_type in ['SST', "static"]:
            col_type = cmp.CollectorTypeSST(**type_dict)
        elif test_type in ['QDT', "dynamic"]:
            col_type = cmp.CollectorTypeQDT(**type_dict)
        else:
            raise ConfigurationError(
                "CollectorType test_type parameter must be one of 'SST', 'static', 'QDT' or 'dynamic'")
        collectors[i] = crd.create_component(sess, col_type)
    sess.commit()

    return collectors


@config_router.get("/collectors/{id}",
                   response_model=smodels.CollectorType,
                   tags=["collectors"],
                   summary="Get a single collector type by id")
def get_collector_type(id: int,
                       sess: Session = Depends(session),
                       crd=Depends(crud)):
    return crd.get_components(sess, cmp.CollectorType, id=id)


@config_router.post("/collectors/{id}",
                    response_model=smodels.CollectorType,
                    tags=["collectors"],
                    summary="Update a collector")
def update_collector(id: int,
                     collector_update: smodels.CollectorType,
                     sess: Session = Depends(session),
                     crd=Depends(crud)):
    collector = crd.get_components(sess, cmp.CollectorType, id=id)
    collector = update_obj(collector, collector_update)

    all_arrays = crd.get_components(sess, cmp.Array)
    all_arrays = all_arrays if isinstance(all_arrays, list) else [all_arrays]
    unique_plants = {a.plant for a in all_arrays if a.collector_type == collector and a.plant is not None}

    for plant in unique_plants:
        plant = update_plant(plant)
        crd.update_component(sess, plant)

    return crd.update_component(sess, collector)


@config_router.delete("/collectors/{id}",
                      status_code=204,
                      tags=["collectors"],
                      summary="Delete a single collector type by id")
def delete_collector_type(id: int,
                          sess: Session = Depends(session),
                          crd=Depends(crud)):
    collector = crd.get_components(sess, cmp.CollectorType, id=id)
    crd.delete_component(sess, collector)

    # TODO I guess this needs revision?
    all_arrays = crd.get_components(sess, cmp.Array)
    all_arrays = all_arrays if isinstance(all_arrays, list) else [all_arrays]
    unique_plants = {a.plant for a in all_arrays if a.collector_type == collector and a.plant is not None}
    for plant in unique_plants:
        plant = update_plant(plant)
        crd.update_component(sess, plant, commit=False)


@config_router.get("/sensor_slots",
                   response_model=List[smodels.SensorSlotValidator],
                   tags=["arrays", "plants", "sensor_slots"],
                   summary="Get a list of slot names to which sensors can be assigned for the given component type")
def slot_names(component_type: enum.Enum('col_types', {"Plant": "plant", "Array": "array"}),
               include_virtuals: bool = False):
    if include_virtuals:
        return cmp.__dict__[component_type.name].sensor_slots.values()
    else:
        return cmp.__dict__[component_type.name].get_real_slots()
