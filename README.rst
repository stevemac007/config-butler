Config Butler
=============

.. image:: https://travis-ci.org/stevemac007/config-butler.svg?branch=master
   :target: https://travis-ci.org/stevemac007/config-butler
   :alt: Travis build badge

.. image:: https://coveralls.io/repos/github/stevemac007/config-butler/badge.svg?branch=master
   :target: https://coveralls.io/github/stevemac007/config-butler?branch=master
   :alt: Coveralls build badge

.. image:: https://img.shields.io/pypi/v/configbutler.svg
   :target: https://pypi.python.org/pypi/configbutler/
   :alt: PyPI version badge


This tool is an extensible framework that provides an ability to manage
server configuration files composed from properties available in the
servers environment.

Modern server solutions are comprimised of many components, which we
currently build and manage in a very monolitic way. This tool aims to
inverse the coupling of service configuration in a kind of dependancy
injection workflow.

Configuration
-------------

The tool holds a strong opinion of convention over configuration, but
aims to support extensions a key points to enable integration and
customisation to a wide range of solution requirements.

At its heart is the ``/etc/configbutler`` folder, which contains a
number of service config definitions which drive the framework to
support ``on-boot`` configuration of services.

These service files are enumerated in alphabetical order to provide a
controlled sequence. The theory of design is that different services can
compose different config sets into a single server, allowing the actual
values and configuration to be resolved at runtime.

These service files can contain multiple outputs resolved from a single
set of properties.

The output of the configuration files are templated using jinja, with a
map of parameters used for flow control and replacement.

The properties are resolved through a number of extensible sources such
as:

-  local host information
-  AWS instance tags
-  AWS instance metadata
-  AWS SSM parameter store

``003-example.config``
~~~~~~~~~~~~~~~~~~~~~~

::

   format: 1.0
   properties:

       HOST_NAME: host|hostname
       HOST_MEMORY: host|total_memory
       ENVIRONMENT: aws|tags|aws:cloudformation:stack-name

       appd_enabled: aws|paramstore|${ENVIRONMENT}.appd_enabled

       application_name: string|sample-app
       controller_licence: aws|paramstore|${ENVIRONMENT}/appd/licence
       controller_host: aws|paramstore|${ENVIRONMENT}/appd/controller
       controller_url: string|/
       controller_port: string|1234
       use_ssl: string|true

       jvm_memory: math|multiply|${HOST_MEMORY}|0.8

   files:
       -
         mode: jinja2
         src: /tmp/appdynamics.conf.j2
         dest: /opt/appd/config/appdynamics.conf

       - mode: jinja2
         src: /tmp/setenv.sh.j2
         dest: /usr/local/tomcat7/conf/setenv.sh

And config templates

``/tmp/setenv.sh.j2``
~~~~~~~~~~~~~~~~~~~~~

::

   export JAVA_OPTS="-Xmx {{ jvm_memory }}"

   {% if appd_enabled %}
   export JAVA_OPTS="${JAVA_OPTS} -javaagent:/opt/appd/appd.jar"
   {% endif %}

``/tmp/appdynamics.conf.j2``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   <controller-info>

       <controller-host>{{ controller_host }}.{{ controller_url }}</controller-host>
       <controller-port>{{ controller_port }}</controller-port>
       <controller-ssl-enabled>{{ use_ssl }}</controller-ssl-enabled>
       <enable-orchestration>false</enable-orchestration>
       <unique-host-id></unique-host-id>
       <account-access-key>{{ controller_licence }} </account-access-key>
       <account-name>{{ controller_host }}</account-name>
       <machine-path></machine-path>
       <application-name>{{ application_name }}</application-name>
       <tier-name>{{ tier_name }}</tier-name>
       <node-name>{{ ansible_ec2_hostname }}</node-name>

   </controller-info>

Property functions
------------------

Math functions
~~~~~~~~~~~~~~

Functions that can be used to to manipulate figures to perform basic
calculations

-  ``add`` - adds two parameters together (eg.
   ``math|add|1|${CLUSTER_SIZE}``)
-  ``subtract`` - subtracts the second from the first parameter (eg.
   ``math|subtract|15|${CLUSTER_SIZE}``)
-  ``multiply`` - multiplys the parameters together (eg.
   ``math|multiply|${TOTAL_MEMORY}|0.8``)
-  ``divide`` - divides the first by the second parameter (eg.
   ``math|divide|${TOTAL_MEMORY}|1024``)

*Example usage*

::

   properties:
       HOST_MEMORY: host|total_memory
       sub_memory: math|multiply|${HOST_MEMORY}|0.8
       jvm_memory: math|divide|${sub_memory}|1024

Map lookups
~~~~~~~~~~~

``Un supported (At the moment!)``

Conditionals
~~~~~~~~~~~~

``Un supported (At the moment!)``

Property scope
--------------

host
~~~~

-  ``hostname`` - the local hostname (eg ``host|hostname``)
-  ``fqdn`` - the local fully qualified domain name (eg ``host|fqdn``)
-  ``ipaddress`` - the ipaddress of eth0 (eg ``host|ipaddress``)
-  ``cpu_count`` - the number of available CPU cores (eg
   ``host|cpu_count``)
-  ``total_memory`` - the total memory available (eg
   ``host|total_memory``)

*Example usage*

::

   properties:
       HOSTNAME: host|hostname

aws
~~~

A set of properties that are resolved from AWS scoped services

metadata
^^^^^^^^

-  ``account_id``
-  ``ami_id``
-  ``ami_launch_index``
-  ``availability_zone``
-  ``iam_info``
-  ``instance_action``
-  ``instance_id``
-  ``instance_profile_arn``
-  ``instance_profile_id``
-  ``instance_type``
-  ``private_hostname``
-  ``private_ipv4``
-  ``public_hostname``
-  ``public_ipv4``
-  ``security_groups``
-  ``region``

*Example usage*

::

   properties:
       aws_account_id: aws|metadata|account_id
       aws_region: aws|metadata|region
       instance_type: aws|metadata|instance_type
       internal_ip: aws|metadata|private_ipv4

tags
^^^^

Tag values are lookups to the current host’s tags.

eg. Cloudformation tags

-  ``aws:cloudformation:logical-id``
-  ``aws:cloudformation:stack-id``
-  ``aws:cloudformation:stack-name``

*Example usage*

::

   properties:
       stack_name: aws|tags|aws:cloudformation:stack-name
       monitoring_tags: aws|tags|monitoring


In some locations it has been identified that Tags were not resolvable when the servers were initially launched.
If no tags are returned for the current host (but asked for in configuration) ``configbutler`` assumes they have not been set yet and will wait and retry the tag lookup.

This lookup will occur 5 times, each one doubling the time waited between requests.

::

   ERROR:configbutler:No AWS::tag values found, waiting 1sec to retry.
   ERROR:configbutler:No AWS::tag values found, waiting 2sec to retry.
   ERROR:configbutler:No AWS::tag values found, waiting 4sec to retry.
   ERROR:configbutler:No AWS::tag values found, waiting 8sec to retry.
   ERROR:configbutler:No AWS::tag values found, waiting 16sec to retry.
   ERROR:configbutler:No AWS::tag values found, continuing with no tags.

If eventually no tags are found after 5 attempts, ``configbutler`` will give up and return ``None`` for any additional tag lookup.

paramstore
^^^^^^^^^^

Values looked up from parameter store, where the key may be composed by other resolved variables.

*Example usage*

::

   properties:
       ENVIRONMENT: string|test
       application: string|garden

       splunk_password: aws|paramstore|/Splunk/SplunkPassword
       controller_licence: aws|paramstore|/${application}/${ENVIRONMENT}/AppD/account-access-key
       controller_host: aws|paramstore|/${application}/${ENVIRONMENT}/AppD/controller
