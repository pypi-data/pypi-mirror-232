# QRshare.io CLI

A CLI tool for uploading files with [qrshare.io](https://qrshare.io) service.

It returns a QR-code with a download URL back in the console

## Installation

The package is available at [https://pypi.org/project/qrshare-io-cli/](https://pypi.org/project/qrshare-io-cli/)

Execute the following command
```bash
pip install qrshare-io-cli
```

If you see a warning like this: 
`WARNING: The script qrs is installed in '/usr/local/Cellar/python@3.8/3.8.17/Frameworks/Python.framework/Versions/3.8/bin' which is not on PATH.`,
then add the path specified about to `${PATH}` environment variable.

E.g.
```bash
echo '# Added by qrshare.io-cli' >> ~/.bash_profile
echo 'export PATH="/usr/local/Cellar/python@3.8/3.8.17/Frameworks/Python.framework/Versions/3.8/bin:${PATH}"' >> ~/.bash_profile
echo -e "\n" >> ~/.bash_profile

```

## Usage 

```bash
qrs <filename>
```

**Output**
```bash
Uploading: .gitignore...
                                                                          
                                                                          
    ██████████████    ████████████  ██      ████  ████  ██████████████    
    ██          ██    ██      ████    ██                ██          ██    
    ██  ██████  ██  ████      ██          ████    ████  ██  ██████  ██    
    ██  ██████  ██  ██████      ██████████      ██  ██  ██  ██████  ██    
    ██  ██████  ██  ██████  ██    ██    ██    ████      ██  ██████  ██    
    ██          ██  ████    ██████████████  ██    ████  ██          ██    
    ██████████████  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██████████████    
                    ██████████  ████  ████  ██    ██                      
    ██  ██████████    ██████  ██████████        ██      ██████████        
      ██            ██            ██    ████  ██    ██  ██████████        
      ██    ██████████████            ██    ██  ████████    ██    ██      
      ████  ██    ██            ██  ██  ██████    ██    ████      ████    
    ██████████  ██  ██  ██████    ██          ████  ████  ████  ████      
    ██      ██      ████  ████████████    ██  ████    ██      ████        
    ██  ██████████          ██████    ██    ██  ██  ██    ██████    ██    
      ████████    ██      ██    ██  ████████  ██████    ██      ██████    
    ████      ████████  ██      ██      ██  ████    ██████  ██            
    ██████    ██  ████    ████  ████          ████  ████████  ████████    
    ██    ████████        ██  ██  ████████            ██    ████  ████    
    ██  ████      ████    ██    ██  ██    ████  ████  ████    ████  ██    
    ████  ██  ████  ██  ██    ██████    ██  ████    ██      ██  ██        
    ██    ████      ██    ██  ██████    ██  ██████      ████  ████        
    ██      ██  ██      ██      ████  ██  ██    ██  ██      ██    ██      
    ██  ██  ██    ████  ██    ██  ██  ████  ████████    ██      ██  ██    
    ██        ████  ██  ██████    ██████            ██████████████  ██    
                    ██        ██  ██          ██  ████      ██████  ██    
    ██████████████            ██  ██  ██████    ██  ██  ██  ████          
    ██          ██  ████████████    ██    ████      ██      ██████████    
    ██  ██████  ██  ████████████████  ██    ██      ██████████  ██        
    ██  ██████  ██  ████    ██████████  ██    ██      ██████  ██████      
    ██  ██████  ██  ████      ████    ████  ██  ████████████              
    ██          ██      ████  ██    ██████  ████████        ████  ████    
    ██████████████  ████        ████████    ██    ██    ██        ██      
                                                                          
                                                                          
    ╔══════════════╦══════════════════════════════════════════════════════════╗
    ║     Filename ║ .gitignore                                               ║
    ╠══════════════╬══════════════════════════════════════════════════════════╣
    ║         Size ║ 29 bytes                                                 ║
    ╠══════════════╬══════════════════════════════════════════════════════════╣
    ║ Download URL ║ https://api2.qrshare.io/api/v2/transfer/ddl/m9jQM2Pre06l ║
    ╚══════════════╩══════════════════════════════════════════════════════════╝

```

### Downloading with `cURL`

```bash
curl --content-disposition https://api2.qrshare.io/api/v2/transfer/ddl/m9jQM2Pre06l
```

> Note: make sure to use `--content-disposition` parameter to keep the original filename