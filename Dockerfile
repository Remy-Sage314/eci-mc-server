FROM eclipse-temurin:21 AS jre-build

RUN $JAVA_HOME/bin/jlink \
         --add-modules ALL-MODULE-PATH \
         --strip-debug \
         --no-man-pages \
         --no-header-files \
         --compress=1 \
         --output /javaruntime


FROM python:3.13-slim-bookworm
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"
COPY --from=jre-build /javaruntime $JAVA_HOME

RUN pip install alibabacloud-eci20180808 Flask rcon
COPY . /opt/mc/scripts/
WORKDIR /opt/mc/scripts/
CMD python /opt/mc/scripts/daemon.py && python /opt/mc/scripts/looping.py