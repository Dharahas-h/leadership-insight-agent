import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  CloudUploadRounded,
  DeleteOutline,
  InsertDriveFileOutlined,
  UploadFile,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material';
import {
  Button,
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  LinearProgress,
} from '@mui/material';

const API_BASE_URL = 'http://localhost:8000/api';

const DocumentUploadNew = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch already uploaded files from backend on component mount
  useEffect(() => {
    fetchUploadedFiles();
  }, []);

  const fetchUploadedFiles = async () => {
    return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/files`);
      const filesFromBackend = response.data.map(file => ({
        id: file.id || file.filename,
        name: file.filename || file.name,
        size: file.size || 0,
        type: file.type || file.mimetype || '',
        uploadedAt: file.uploadedAt || file.created_at,
        isExisting: true, // Mark as already uploaded
      }));
      setUploadedFiles(filesFromBackend);
    } catch (err) {
      console.error('Error fetching uploaded files:', err);
      setError('Failed to load uploaded files. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = event => {
    const files = Array.from(event.target.files);
    setError(null);

    // Add files to the list with 'pending' status
    const newFiles = files.map(file => ({
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toISOString(),
      status: 'pending', // pending, uploading, chunking, completed, error
      file: file, // Store the actual file object for later upload
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Reset file input
    event.target.value = null;
  };

  const handleProcessFile = async fileId => {
    const fileToProcess = uploadedFiles.find(f => f.id === fileId);
    if (!fileToProcess || !fileToProcess.file) return;

    try {
      // Update status to uploading
      setUploadedFiles(prev =>
        prev.map(f => (f.id === fileId ? { ...f, status: 'uploading' } : f))
      );

      const formData = new FormData();
      formData.append('file', fileToProcess.file);

      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Update status to chunking
      setUploadedFiles(prev =>
        prev.map(f =>
          f.id === fileId
            ? {
                ...f,
                status: 'chunking',
                id: response.data.id || f.id,
              }
            : f
        )
      );

      // Update status to completed
      setUploadedFiles(prev =>
        prev.map(f =>
          f.id === fileId || f.id === response.data.id
            ? {
                ...f,
                status: 'completed',
                file: null, // Clear file object after successful upload
              }
            : f
        )
      );
    } catch (err) {
      console.error(`Error processing ${fileToProcess.name}:`, err);
      setUploadedFiles(
        prev => f =>
          f.id === fileId
            ? {
                ...f,
                status: 'error',
                errorMessage:
                  err.response?.data?.message || 'Processing failed',
              }
            : f
      );
      setError(`Failed to process ${fileToProcess.name}`);
    }
  };

  const handleRemoveFile = async fileId => {
    try {
      // Call backend API to delete the file
      await axios.delete(`${API_BASE_URL}/files/${fileId}`);
      setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
    } catch (err) {
      console.error('Error deleting file:', err);
      setError('Failed to delete file. Please try again.');
    }
  };

  const formatFileSize = bytes => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusDisplay = status => {
    switch (status) {
      case 'pending':
        return { text: 'Ready to upload', color: 'default', icon: null };
      case 'uploading':
        return {
          text: 'Uploading...',
          color: 'info',
          icon: <CircularProgress size={16} />,
        };
      case 'chunking':
        return {
          text: 'Processing & Chunking...',
          color: 'warning',
          icon: <CircularProgress size={16} />,
        };
      case 'completed':
        return {
          text: 'Completed',
          color: 'success',
          icon: <CheckCircle fontSize="small" />,
        };
      case 'error':
        return {
          text: 'Failed',
          color: 'error',
          icon: <ErrorIcon fontSize="small" />,
        };
      default:
        return { text: 'Unknown', color: 'default', icon: null };
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 600 }}>
      <Button
        component="label"
        variant="contained"
        tabIndex={-1}
        startIcon={<CloudUploadRounded />}
        sx={{ mb: 2 }}
      >
        Select files
        <input
          type="file"
          hidden
          multiple
          onChange={handleFileSelect}
          accept=".pdf,.doc,.docx,.txt,.csv,.xlsx,.xls"
        />
      </Button>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && uploadedFiles.length === 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {uploadedFiles.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Documents ({uploadedFiles.length})
          </Typography>
          <List>
            {uploadedFiles.map(file => {
              const statusDisplay = getStatusDisplay(file.status);
              return (
                <ListItem
                  key={file.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    bgcolor: 'background.paper',
                    flexDirection: 'column',
                    alignItems: 'stretch',
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      width: '100%',
                      alignItems: 'center',
                    }}
                  >
                    <ListItemIcon>
                      <InsertDriveFileOutlined color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={
                        <Box
                          sx={{
                            display: 'flex',
                            gap: 1,
                            alignItems: 'center',
                            mt: 0.5,
                            flexWrap: 'wrap',
                          }}
                        >
                          <Chip
                            label={formatFileSize(file.size)}
                            size="small"
                            variant="outlined"
                          />
                          {file.type && (
                            <Chip
                              label={
                                file.type.split('/')[1]?.toUpperCase() || 'FILE'
                              }
                              size="small"
                              variant="outlined"
                            />
                          )}
                          <Chip
                            icon={statusDisplay.icon}
                            label={statusDisplay.text}
                            size="small"
                            color={statusDisplay.color}
                            variant="outlined"
                          />
                        </Box>
                      }
                    />
                    <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
                      {file.status === 'pending' && (
                        <Button
                          variant="contained"
                          size="small"
                          startIcon={<UploadFile />}
                          onClick={() => handleProcessFile(file.id)}
                        >
                          Upload
                        </Button>
                      )}
                      {file.status !== 'uploading' &&
                        file.status !== 'chunking' && (
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleRemoveFile(file.id)}
                            color="error"
                          >
                            <DeleteOutline />
                          </IconButton>
                        )}
                    </Box>
                  </Box>
                  {(file.status === 'uploading' ||
                    file.status === 'chunking') && (
                    <Box sx={{ width: '100%', mt: 1 }}>
                      <LinearProgress />
                    </Box>
                  )}
                  {file.status === 'error' && file.errorMessage && (
                    <Typography
                      variant="caption"
                      color="error"
                      sx={{ mt: 1, ml: 7 }}
                    >
                      {file.errorMessage}
                    </Typography>
                  )}
                </ListItem>
              );
            })}
          </List>
        </Box>
      )}
    </Box>
  );
};

export default DocumentUploadNew;
