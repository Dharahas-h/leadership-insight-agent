import { useState } from 'react';
import axios from 'axios';
import './DocumentUpload.css';

const DocumentUpload = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  // Track status for each file: 'pending', 'uploading', 'success', 'error'
  const [fileStatuses, setFileStatuses] = useState({});

  const handleDrag = e => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const extractFiles = fileList => {
    if (!fileList) return [];
    return Array.from(fileList).filter(Boolean);
  };

  const handleDrop = e => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = extractFiles(e.dataTransfer.files);
    if (files.length) {
      setSelectedFiles(files);
      setUploadStatus('');
      // Initialize status for new files
      const newStatuses = {};
      files.forEach((file, index) => {
        newStatuses[index] = 'pending';
      });
      setFileStatuses(newStatuses);
    }
  };

  const handleFileSelect = e => {
    const files = extractFiles(e.target.files);
    if (files.length) {
      setSelectedFiles(files);
      setUploadStatus('');
      // Initialize status for new files
      const newStatuses = {};
      files.forEach((file, index) => {
        newStatuses[index] = 'pending';
      });
      setFileStatuses(newStatuses);
    }
  };

  const removeFile = index => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setFileStatuses(prev => {
      const newStatuses = {};
      Object.keys(prev).forEach(key => {
        const keyIndex = parseInt(key);
        if (keyIndex < index) {
          newStatuses[keyIndex] = prev[keyIndex];
        } else if (keyIndex > index) {
          newStatuses[keyIndex - 1] = prev[keyIndex];
        }
      });
      return newStatuses;
    });
    setUploadStatus('');
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) return;

    setLoading(true);
    setUploadStatus('');

    let successCount = 0;
    let errorCount = 0;

    // Upload each file individually
    for (let index = 0; index < selectedFiles.length; index++) {
      const file = selectedFiles[index];

      // Update status to 'uploading'
      setFileStatuses(prev => ({
        ...prev,
        [index]: 'uploading',
      }));

      const formData = new FormData();
      formData.append('file', file);

      try {
        await axios.post('http://localhost:8000/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Update status to 'success'
        setFileStatuses(prev => ({
          ...prev,
          [index]: 'success',
        }));
        successCount++;
      } catch (error) {
        console.error(`Upload error for ${file.name}:`, error);
        // Update status to 'error'
        setFileStatuses(prev => ({
          ...prev,
          [index]: 'error',
        }));
        errorCount++;
      }
    }

    // Set overall upload status
    if (errorCount === 0) {
      setUploadStatus(`✅ All ${successCount} file(s) uploaded successfully!`);
    } else if (successCount === 0) {
      setUploadStatus(`❌ All ${errorCount} file(s) failed to upload.`);
    } else {
      setUploadStatus(
        `⚠️ ${successCount} file(s) uploaded, ${errorCount} failed.`
      );
    }

    setLoading(false);
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <h2>📄 Upload Leadership Documents</h2>
        <p className="upload-description">
          Upload documents for analysis. Supported formats: PDF, DOCX, TXT, MD
        </p>

        <div
          className={`drop-zone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="drop-zone-icon">📁</div>
          <p className="drop-zone-text">Drag and drop your files here</p>
          <label className="file-label">
            <input
              type="file"
              multiple
              onChange={handleFileSelect}
              accept=".pdf,.docx,.doc,.txt,.md"
              className="file-input"
            />
            <span className="browse-button">Browse Files</span>
          </label>
        </div>

        {selectedFiles.length > 0 && (
          <div className="selected-file">
            {selectedFiles.map((file, index) => {
              const status = fileStatuses[index] || 'pending';
              const statusIcon = {
                pending: '⏳',
                uploading: '⏫',
                success: '✅',
                error: '❌',
              }[status];
              const statusText = {
                pending: 'Pending',
                uploading: 'Uploading...',
                success: 'Uploaded',
                error: 'Failed',
              }[status];

              return (
                <div
                  key={`${file.name}-${file.size}-${index}`}
                  className="file-info"
                >
                  <span className="file-icon">📎</span>
                  <div className="file-details">
                    <p className="file-name">{file.name}</p>
                    <p className="file-size">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <div className={`file-upload-status status-${status}`}>
                    {statusIcon} {statusText}
                  </div>
                  <button
                    className="remove-button"
                    onClick={() => removeFile(index)}
                    disabled={status === 'uploading'}
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>
        )}

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={!selectedFiles.length || loading}
        >
          {loading
            ? 'Uploading...'
            : `Upload Document${selectedFiles.length > 1 ? 's' : ''}`}
        </button>

        {uploadStatus && (
          <div
            className={`upload-status ${uploadStatus.startsWith('✅') ? 'success' : 'error'}`}
          >
            {uploadStatus}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
