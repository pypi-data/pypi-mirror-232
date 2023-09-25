# apsis-ocr
![logo](./deployment/images/apsis.png) 

Apsis-OCR is a Mixed language ocr system for Printed Documents developed at [Apsis Solutions limited](https://apsissolutions.com/)

The full system is build with 3 components: 
* Text detection : DBNet
* Text recognition:
    * Bangla Text : ApsisNet
    * English Text : SVTR-LCNet
* Text classification : DenseNet121    

# **Installation**
## **As module/pypi package**
* install apsis-ocr

```
pip install apsisocr
```

## **Building from source : Linux/Ubuntu**

* **clone the repository** : 
```
git clone https://github.com/mnansary/apsis-ocr.git
```

* **Installing conda**: 

```
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

* **create a conda environment**: 

```
conda create -n apsisocr python=3.9
```

* **activate conda environment**: 

```
conda activate apsisocr

```
* **cpu installation**  :

```
bash install.sh cpu
``` 
* **gpu installation**  :
    
```
bash install.sh gpu
``` 



# **Deployment**

```python
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
nohup python api_ocr.py & # deploys at port 3032 by defautl
nohup streamlit run app.py --server.port 3033 & # deploys streamlit built frontend at 3033 port
```

**TESTED GPU INFERENCE SERVER CONFIG**  

```python
OS          : Ubuntu 20.04.6 LTS      
Memory      : 62.4 GiB 
Processor   : Intel® Xeon(R) Silver 4214R CPU @ 2.40GHz × 24    
Graphics    : NVIDIA RTX A6000/PCIe/SSE2
Gnome       : 3.36.8
```