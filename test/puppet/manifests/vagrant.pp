#
# Playdoh puppet magic for dev boxes
#
import "classes/*.pp"

$RABBITMQ_VHOST = '/'
$RABBITMQ_HOST = 'localhost'
$RABBITMQ_PORT = '5672'

Exec {
    path => "/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin",
}

class dev {
    class {
        init: before => Class[rabbitmq];
        rabbitmq:;
    }
}

include dev
