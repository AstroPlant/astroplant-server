================================
AstroPlant backend documentation
================================

The AstroPlant backend is a platform to coordinate and control multiple
growth systems over the internet. The backend is designed to be used
with AstroPlant kits, but any growth system implementing the API is
supported.

About this documentation
========================

This documentation gives the technical details to deploy, change, and
improve the system. If you are looking for information on using the
AstroPlant system, see the 
`AstroPlant build guide <https://astroplant.gitbooks.io/building-an-astroplant-kit>`_.

Project overview
================

The platform is built on the Django web framework, and is split into
three projects:

1. The server
    contains the configuration of the system
    
2. The backend
    contains the growth system data models and logic
    
3. The website
    contains controllers and views to interact with growth systems and see their data
    
.. toctree::
   :maxdepth: 1
   :caption: Contents
   
   Models <models/index>
   Permissions <misc/permissions>
   Modules <modules/modules>
   
Installation instructions
=========================

For installation instructions, see the
`project repository <https://github.com/AstroPlant/astroplant-server>`_.
   
Other
=====
   
* :ref:`search`
