# Config Butler

This tool is an extensible framework that provides an ability to manage server configuration files composed from properties available in the servers environment.

Modern server solutions are comprimised of many components, which we currently build and manage in a very monolitic way.
This tool aims to inverse the coupling of service configuration in a kind of dependancy injection workflow.

## Configuration

The tool holds a strong opinion of convention over configuration, but aims to support extensions a key points to enable integration and customisation to a wide range of solution requirements.

At its heart is the `/etc/configbutler` folder, which contains a number of service config definitions which drive the framework to support `on-boot` configuration of services.

These service files are enumerated in alphabetical order to provide a controlled sequence.  The theory of design is that different services can compose different config sets into a single server, allowing the actual values and configuration to be resolved at runtime.

These service files can contain multiple outputs resolved from a single set of properties.

The output of the configuration files are templated using jinja, with a map of parameters used for flow control and replacement.

The properties are resolved through a number of extensible sources such as:

* local host information
* AWS instance tag values
*


### `003-example.config`

```
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
      src: file:///tmp/appdynamics.conf.j2
      dest: /opt/appd/config/appdynamics.conf

    - mode: jinja2
      src: file:///tmp/setenv.sh.j2
      dest: /usr/local/tomcat7/conf/setenv.sh

    - mode: jinja2
      src: s3://example-bucket/${ENVIRONMENT}/application.conf.j2
      dest: /etc/application/application.conf
```

And config templates

### `/usr/local/tomcat7/conf/setenv.sh`

```
export JAVA_OPTS="-Xmx {{ jvm_memory }}"

{% if appd_enabled %}
export JAVA_OPTS="${JAVA_OPTS} -javaagent:/opt/appd/appd.jar"
{% endif %}
```


### `/opt/appd/config/appdynamics.conf`

```
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

```

## Property functions

### Math functions

Functions that can be used to to manipulate figures to perform basic calculations

* `add` - adds two parameters together (eg. math|add|1|${CLUSTER_SIZE})
* `subtract` - subtracts the second from the first parameter (eg. math|subtract|15|${CLUSTER_SIZE}
* `multiply` - multiplys the parameters together (eg. math|multiply|${TOTAL_MEMORY}|0.8
* `divide` - divides the first by the second parameter (eg. math|divide|${TOTAL_MEMORY}|1024

```
properties:
    HOST_MEMORY: host|total_memory
    sub_memory: math|multiply|${HOST_MEMORY}|0.8
    jvm_memory: math|divide|${sub_memory}|1024
```

### Map lookups

`Un supported (At the moment!)`

### Conditionals

`Un supported (At the moment!)`

## Property scope

### host

* `hostname` -
* `ipaddress` -
* `cpu_count` -
* `total_memory` -

```
properties:
    HOSTNAME: host|hostname
```


### aws

A set of properties that are resolved from AWS scoped services

#### metadata

* `account_id`
* `ami_id`
* `ami_launch_index`
* `availability_zone`
* `iam_info`
* `instance_action`
* `instance_id`
* `instance_profile_arn`
* `instance_profile_id`
* `instance_type`
* `private_hostname`
* `private_ipv4`
* `public_hostname`
* `public_ipv4`
* `security_groups`
* `region`

#### tags

Tag values are lookups to the current host's tags,

eg. Cloudformation tags

* `aws:cloudformation:logical-id`
* `aws:cloudformation:stack-id`
* `aws:cloudformation:stack-name`

#### paramstore

Values looked up from parameter store, where the key may be composed by other resolved variables.