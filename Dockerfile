# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM python:3.12 as build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg libavcodec-extra && \
    pip install pydub && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy function code and MP3 file
RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}


RUN chmod -R 755 ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
        awslambdaric \
        -r ${FUNCTION_DIR}/requirements.txt

# Use a slim version of the base Python image to reduce the final image size
FROM python:3.12-slim

# Install FFmpeg in the final image as well
RUN apt-get update && \
    apt-get install -y ffmpeg libavcodec-extra && \
    pip install pydub && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

RUN chmod -R 755 ${FUNCTION_DIR}



# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "lambda_function.handler" ]


# Windows app
# docker build -t win_app:test .
# docker run -it -v $(pwd):/function --name local_win win_app:test bash
# docker build -t win_app:test -f Dockerfile_win .




