import React, { useRef, useState, ChangeEvent, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

import Webcam from 'react-webcam';


function App() {
  const webcamRef = useRef<Webcam>(null);
  const [selfie, setSelfie] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  // const [pyodide, setPyodide] = useState<any>(null);
  // const [features, setFeatures] = useState<number[] | null>(null);

  // useEffect(() => {
  //   const loadPyodide = async () => {
  //     if (window.loadPyodide) {
  //       const pyodide = await window.loadPyodide();
  //       await pyodide.loadPackage(['numpy', 'Pillow', 'facenet-pytorch', 'torch', 'opencv-python']);
  //       setPyodide(pyodide);
  //     } else {
  //       console.error('Pyodide is not loaded');
  //     }
  //   };

  //   loadPyodide();
  // }, []);


  const captureSelfie = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      console.log("selfie image stored in client", imageSrc)
      setSelfie(imageSrc);
    }
  };

  const handleUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        console.log("upload image stored in client", reader.result as string)
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const processImage = async () => {

    try {
      const response = await fetch('http://127.0.0.1:5000/process_images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          images: [uploadedImage, selfie],
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      console.log(result)
      // setFeatures(result);
    } catch (error) {
      console.error('Error processing images:', error);
    }
  };

  return (
    <div className="App">
      <div style={styles.container}>
      <div style={styles.cameraContainer}>
        {
          !selfie && (
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              style={styles.webcam}
            />
          )
        }
        {
          !selfie && (
            <button onClick={captureSelfie} style={styles.button}>Take Selfie</button>
          )
        }
        {
          !uploadedImage && (
            <div>
              <input id="upload-input" type="file" onChange={handleUpload} style={styles.uploadInput} />
              <label htmlFor="upload-input" style={styles.uploadLabel}>Upload Picture</label>
            </div>
          )
        }
        
      </div>
      <div style={styles.imageContainer}>
        {selfie && (
          <div>
            <h3>Selfie</h3>
            <img src={selfie} alt="Selfie" style={styles.image} />
          </div>
        )}
        {uploadedImage && (
          <div>
            <h3>Uploaded Image</h3>
            <img src={uploadedImage} alt="Uploaded" style={styles.image} />
          </div>
        )}
        {uploadedImage && selfie && (
           <button onClick={processImage} style={styles.button}>Process Images</button>
        )}

      </div>
    </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    // backgroundColor: '#f0f0f0',
  },
  cameraContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    marginBottom: '20px',
  },
  webcam: {
    width: '320px',
    height: '240px',
    borderRadius: '5px',
    marginBottom: '10px',
  },
  button: {
    padding: '10px 20px',
    margin: '20px',
    borderRadius: '5px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
  },
  uploadInput: {
    display: 'none',
  },
  uploadLabel: {
    padding: '10px 20px',
    margin: '10px',
    borderRadius: '5px',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
  },
  imageContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
  },
  image: {
    width: '320px',
    height: '240px',
    borderRadius: '5px',
    marginBottom: '10px',
  },
};

export default App;
