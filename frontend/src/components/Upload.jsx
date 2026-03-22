import { useState, useCallback, useEffect } from 'react';
import { Button, Paper, Typography, LinearProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import './Upload.css';
import axios from 'axios';
import { Delete } from '@mui/icons-material';

function FileCard({ file, onUpload, onDelete, isCompleted }) {
  const [loading, setLoading] = useState(false);
  const [progressText, setProgressText] = useState('');
  const [completed, setCompleted] = useState(isCompleted);
  const [documentId, setDocumentId] = useState(file['documentId'] || null);

  const formatFileSize = bytes => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const handleDelete = async () => {
    const response = await axios.delete(
      `http://localhost:8000/document/delete/${documentId}`
    );
    console.log('Delete Response', response);
    onDelete();
  };

  const handleUpload = async () => {
    setLoading(true);
    setProgressText('Starting upload...');

    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(
      'http://localhost:8000/document/upload/',
      formData
    );
    const data = response.data;

    // Simulated streaming (replace with real backend stream)
    const embedStream = new EventSource(
      `http://localhost:8000/document/embed/${data['document_id']}`
    );
    embedStream.onmessage = event => {
      const eventData = JSON.parse(event.data);
      console.log('message', eventData);
      if (eventData['status'] == 'completed') {
        setLoading(false);
        setCompleted(true);
        onUpload(file);
        embedStream.close();
      } else {
        setProgressText(eventData['message'] || 'Random Message...');
      }
    };

    setDocumentId(data['document_id']);
    // const fakeStream = [
    //   'Uploading file...',
    //   'Processing document...',
    //   'Analyzing content...',
    //   'Extracting insights...',
    //   'Finalizing...',
    //   'Completed!',
    // ];

    // for (let msg of fakeStream) {
    //   await new Promise(res => setTimeout(res, 800));
    //   setProgressText(msg);
    // }
  };

  return (
    <Paper className="file-card">
      <div className="file-info">
        <InsertDriveFileIcon className="file-icon" />
        <div className="file-details">
          <Typography className="file-name">{file.name}</Typography>
          <div className="file-meta">
            <Typography className="file-type">
              {file.type || 'Unknown type'}
            </Typography>
            <Typography className="file-size">
              {formatFileSize(file.size)}
            </Typography>
          </div>
        </div>
        {completed ? (
          <Button
            className="upload-button"
            variant="contained"
            startIcon={<Delete />}
            onClick={handleDelete}
            disabled={loading}
          >
            {loading ? 'Uploading...' : 'Delete'}
          </Button>
        ) : (
          <Button
            className="upload-button"
            variant="contained"
            startIcon={<CloudUploadIcon />}
            onClick={handleUpload}
            disabled={loading || completed}
          >
            {loading ? 'Uploading...' : 'Upload File'}
          </Button>
        )}
      </div>

      {loading && (
        <div className="progress-section">
          <LinearProgress className="progress-bar" />
          <Typography className="progress-text">{progressText}</Typography>
        </div>
      )}

      {completed && (
        <div className="success-message">
          <CheckCircleIcon />
          <span>Upload completed successfully!</span>
        </div>
      )}
    </Paper>
  );
}

export default function Upload() {
  const [files, setFiles] = useState([]);

  const loadDocuments = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/document/embedded-docs'
      );
      console.log('Response', response);
      if (response.status == 200) {
        const data = JSON.parse(response.data);
        const documentIds = Object.keys(data);
        const newFiles = [];
        documentIds.forEach(id => {
          const file = data[id];
          newFiles.push({
            documentId: file['document_id'],
            name: file['filename'],
            type: file['type'],
            size: file['size'],
            isCompleted: true,
          });
        });
        setFiles([...files, ...newFiles]);
      }
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleDrop = useCallback(event => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files);
    setFiles(prev => [...prev, ...droppedFiles]);
  }, []);

  const handleDelete = index => {
    const newFiles = files.filter((_, i) => i != index);
    setFiles(newFiles);
  };

  const handleDragOver = event => {
    event.preventDefault();
  };

  const handleFileSelect = event => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const handleUploadComplete = file => {
    console.log('Uploaded:', file.name);
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <h1 className="upload-title">Leadership Insights</h1>
        <p className="upload-subtitle">
          Upload your documents to gain valuable insights
        </p>
      </div>

      <Paper
        className="drop-zone"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <CloudUploadIcon className="drop-zone-icon" />
        <Typography className="drop-zone-text">
          Drag & Drop your files here
        </Typography>
        <Typography className="drop-zone-subtext">
          or click below to browse
        </Typography>
        <Button className="browse-button" variant="contained" component="label">
          Browse Files
          <input type="file" hidden multiple onChange={handleFileSelect} />
        </Button>
      </Paper>

      {files.length > 0 && (
        <div className="files-section">
          <div className="files-header">
            <FolderOpenIcon />
            Selected Files
            <span className="files-count">{files.length}</span>
          </div>
          {files.map((file, index) => (
            <FileCard
              key={index}
              file={file}
              isCompleted={file.isCompleted || false}
              onUpload={handleUploadComplete}
              onDelete={() => handleDelete(index)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
