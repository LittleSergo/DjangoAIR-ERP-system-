# DjangoAir ERP system

This project is a service application for airline management.

This service have two independent web interfaces. 
One interface is in use by customers. Another interface is in use by staff. 

## Customer interface

The customer interface is very simple. 
There clients can find the flights and buy tickets.
Also, the customer have a personal cabinet. 
The personal cabinet shows information about the future and previous flights, 
and provides service for online check-in.

It also has an API.

## Staff interface

The staff interface is grant access by roles:
* Gate manager
* Check-in manager
* Supervisor

Gate manager can register the boarding of the passenger at the gate using the ticket code.

Check-in manager makes check-in passenger, add options and take a fee for luggage.

The supervisor can do everything that do gate manager and check-in manager. 
And he can add or remove the gate manager and check-in manager. 
Also, he can create and delete a flight, options, planes and manage discounts.

## Deployment

This project has configured docker deployment. It has 3 main django applications: 
client, staff and client API which deploys separately each in their own container. 
Also project starts one PostgreSQL container for all django applications.
Staff and client apps have celery end each celery worker, beat and flower runs 
in separate container, and in addition each celery have their own containers with redis.
Each django app connected to separate containers with redis for cache.
There is also a container with nginx that handles the server routine.

## common instances

Django apps in this project have common_instances app inside each of projects.
This app includes database models which is used in each django app.
It's located in separate [repository](https://github.com/LittleSergo/common_instances)
(in the repository you can find instructions how to use it). 
Common instances app was added to requirements.txt files in django apps in this project.
