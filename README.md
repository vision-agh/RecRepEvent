Build and run docker:

'''
docker build -t rec-rep .
docker run -it --rm --gpus all -v $(pwd):/workspace -w /workspace my-dev-env
'''