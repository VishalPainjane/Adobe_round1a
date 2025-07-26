docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .

docker run --rm -v ${PWD}/input:/Draft1/input -v ${PWD}/output:/Draft1/output --network none mysolutionname:somerandomidentifier