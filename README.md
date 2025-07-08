# How to Run Prometheus Using Lepton Injector & Earth Model Svc

## Setting up the environment

First we need a consistent conda environment for the installation that follows

```bash=
conda create --name prom_env -c conda-forge python=3.11
conda activate prom_env
conda install -c conda-forge boost boost-cpp h5py matplotlib photospline suitesparse cfitsio cmake ipykernel jupyter
python3 -m pip install proposal
```
Next, time to download & install the packages

## Lepton Injector

### Installing LeptonInjector

```bash=
cd ~
mkdir lepinj
cd lepinj
git clone https://github.com/icecube/LeptonInjector.git
mv LeptonInjector source
cd source
git checkout b5ab876
```

Now we must be careful to compile with thr proper `CMakeLists.txt` file inside
`~/lepinj/source`

Use the `CMakeLists.txt` provided with this github repo; the default **LeptonInjector** doesn't compile `EarthModelService`

```bash=
cd ~/lepinj/source/
vim CMakeLists.txt
cd ..
#The step above is used to fix the CMake file for proper shared object compilation
mkdir build install
```

In the same conda environment, issue these commands:

```bash=
cd ~/lepinj/build
export CONDA_PREFIX=/home/$USER/anaconda3/envs/prom_env
$CONDA_PREFIX/bin/cmake \
  -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX \
  -DCMAKE_PREFIX_PATH=$CONDA_PREFIX    \
  -DCMAKE_POLICY_DEFAULT_CMP0074=NEW   \
  -DCMAKE_POLICY_DEFAULT_CMP0167=NEW   \
  -DCMAKE_POLICY_VERSION_MINIMUM=4.0  \
  -DPython_ROOT_DIR=$CONDA_PREFIX      \
  ../source
make -j($nproc) && make install
```
Don't do sudo make install; not needed because it installas stuff into system bin path.

## Installing Prometheus

```bash=
cd ~
git clone https://github.com/Harvard-Neutrino/prometheus.git
cd prometheus
git checkout e072a5f
pip install -e .
```
We need to make some edits inside the prometheus package. It needs a line replacement.

```bash=
cd ~/prometheus/prometheus/injection
vim lepton_injector_utils.py

```
Matching the function definitions, please make a single line edit as below

```bash=
earth_model_dir = "/".join(path_dict["earth model location"].split("/")[:-2]) + "/"
    earth_model_name = path_dict["earth model location"].split("/")[-1].split(".")[0]
    earth = em.EarthModelService(
        "Zorg",
        earth_model_dir,
        [earth_model_name],
        ["Standard"],
        "NoIce",
        0.0,
        -detector_offset[2]
    )
    # Replace
    # controller.SetEarthModelService(earth)
    # by the uncommented line below
    controller.SetEarthModel("Zorg", earth_model_dir)
    # Other stuff in your script as usual.
```
Then, do the following:

```bash=
cd ~/prometheus/resources/earthparams/densities/
ls PREM_mmc.dat
# IF PREM_mmc.dat doesn't show up, do, to have a PREM card to run (for example)
cp PREM_south_pole.dat PREM_mmc.dat
```
Next, go to the examples directory inside prometheus,
 `cd ~/prometheus/examples/`

Ensure that your `conda environment` is active,
copy the python script from this repo (`test-sim.py` to `~/prometheus/examples/`) and finally run the python script  in this repo as
`python3 test-sim.py` within the `examples` directory.

This will create a folder `output` in `~/prometheus/examples/` with `h5 & parquet` files on successful run.

Prometheus must be isntalled in the same terminal `tty` session.

If not, do, before you run the simulation:
```bash=
cd ~/prometheus
pip install -e .
```









