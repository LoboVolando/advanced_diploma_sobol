FROM fluent/fluentd:v1.14.0-debian-1.0
USER root
RUN ["fluent-gem", "install", "fluent-plugin-elasticsearch"]
USER fluent
#RUN ["gem", "search", "-rd", "fluent-plugin"]