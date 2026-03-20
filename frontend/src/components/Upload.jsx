import { Box, Button, Paper, Typography, LinearProgress } from '@mui/material';
import React, { useState, useCallback } from 'react';

import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const beigeTheme = {
  background: '#f5f5dc',
  border: '#d2b48c',
  text: '#5c4033',
};

function FileCard({ file, onUpload }) {
  const [loading, setLoading] = useState(false);
  const [progressText, setProgressText] = useState('');

  const handleUpload = async () => {
    setLoading(true);
    setProgressText('Starting upload...');

    // Simulated streaming (replace with real backend stream)
    const fakeStream = [
      'Uploading file...',
      'Processing document...',
      'Analyzing content...',
      'Finalizing...',
      'Completed!',
    ];

    for (let msg of fakeStream) {
      await new Promise(res => setTimeout(res, 800));
      setProgressText(msg);
    }

    setLoading(false);
    onUpload(file);
  };

  return (
    <Paper
      sx={{
        p: 2,
        mb: 2,
        backgroundColor: beigeTheme.background,
        border: `1px solid ${beigeTheme.border}`,
      }}
    >
      <Typography sx={{ color: beigeTheme.text }}>
        <strong>Name:</strong> {file.name}
      </Typography>
      <Typography sx={{ color: beigeTheme.text }}>
        <strong>Type:</strong> {file.type || 'Unknown'}
      </Typography>

      <Box mt={2}>
        <Button
          variant="contained"
          startIcon={<CloudUploadIcon />}
          onClick={handleUpload}
          disabled={loading}
          sx={{
            backgroundColor: '#d2b48c',
            color: '#5c4033',
            '&:hover': { backgroundColor: '#c19a6b' },
          }}
        >
          {loading ? 'Uploading...' : 'Upload'}
        </Button>
      </Box>

      {loading && (
        <Box mt={2}>
          <LinearProgress />
          <Typography sx={{ mt: 1, color: beigeTheme.text }}>
            {progressText}
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

export default function Upload() {
  const [files, setFiles] = useState([]);

  const handleDrop = useCallback(event => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files);
    setFiles(prev => [...prev, ...droppedFiles]);
  }, []);

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
    <Box p={4}>
      <Paper
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        sx={{
          p: 4,
          textAlign: 'center',
          border: `2px dashed ${beigeTheme.border}`,
          backgroundColor: beigeTheme.background,
          cursor: 'pointer',
        }}
      >
        <Typography sx={{ color: beigeTheme.text, mb: 2 }}>
          Drag & Drop files here
        </Typography>
        <Button
          variant="outlined"
          component="label"
          sx={{ borderColor: beigeTheme.border, color: beigeTheme.text }}
        >
          Browse Files
          <input type="file" hidden multiple onChange={handleFileSelect} />
        </Button>
      </Paper>

      <Box mt={4}>
        {files.map((file, index) => (
          <FileCard key={index} file={file} onUpload={handleUploadComplete} />
        ))}
      </Box>
    </Box>
  );
}
