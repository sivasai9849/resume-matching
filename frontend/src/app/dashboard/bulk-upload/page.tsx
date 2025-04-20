"use client";
import React, { useState } from "react";
import BreadcrumbDashboard from "@/app/dashboard/components/layouts/BreadcrumbDashboard";
import HeadMain from "@/app/components/HeadMain";
import { Button, Paper, Typography, Box, Alert } from "@mui/material";
import { MdCloudUpload, MdFileDownload } from "react-icons/md";
import { ToastContainer, toast } from "react-toastify";
import useAxios from "@/app/services/useAxios";
import * as XLSX from "xlsx";

const BulkUploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);

  // Function to download template
  const handleDownloadTemplate = () => {
    // Create workbook with the required fields
    const workbook = XLSX.utils.book_new();
    const templateData = [
      ["candidate_name", "email", "phone_number", "department", "has_resume", "comment"],
      ["John Doe", "john@example.com", "+1234567890", "Engineering", "FALSE", "Experienced frontend developer"],
      ["Jane Smith", "jane@example.com", "+0987654321", "Marketing", "TRUE", "5 years marketing experience"],
      ["Robert Brown", "robert@example.com", "+1122334455", "Sales", "FALSE", "New graduate seeking sales position"],
    ];
    
    const worksheet = XLSX.utils.aoa_to_sheet(templateData);
    
    // Format phone numbers and boolean fields
    const phoneNumberCells = ['C2', 'C3', 'C4']; // Column C rows 2-4
    const booleanCells = ['E2', 'E3', 'E4']; // Column E rows 2-4
    
    // Set phone numbers as text
    phoneNumberCells.forEach(cell => {
      if (worksheet[cell]) {
        worksheet[cell].t = 's'; // Set type to string
      }
    });
    
    // Set boolean fields as text
    booleanCells.forEach(cell => {
      if (worksheet[cell]) {
        worksheet[cell].t = 's'; // Set type to string
      }
    });
    
    // Add the worksheet to the workbook
    XLSX.utils.book_append_sheet(workbook, worksheet, "Candidates");
    
    // Generate the Excel file as a binary string
    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
    
    // Create a Blob from the buffer
    const blob = new Blob([excelBuffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    
    // Create a download link and trigger the download
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "candidate_template.xlsx";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success("Template downloaded successfully!");
  };

  // Function to handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Check if the file is an Excel file
      if (!selectedFile.name.endsWith('.xlsx') && !selectedFile.name.endsWith('.xls')) {
        toast.error("Please select a valid Excel file (.xlsx or .xls)");
        return;
      }
      
      setFile(selectedFile);
      
      // Read the file content for preview
      const reader = new FileReader();
      reader.onload = (evt) => {
        try {
          const data = new Uint8Array(evt.target?.result as ArrayBuffer);
          const workbook = XLSX.read(data, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          
          // Validate required fields in the Excel file
          const requiredFields = ['candidate_name', 'email', 'phone_number', 'department'];
          const firstRow = jsonData[0] || {};
          const missingFields = requiredFields.filter(field => !Object.keys(firstRow).includes(field));
          
          if (missingFields.length > 0) {
            toast.error(`Missing required fields: ${missingFields.join(', ')}`);
            setFile(null);
            return;
          }
          
          setPreview(jsonData.slice(0, 5)); // Show first 5 rows in preview
          setShowPreview(true);
        } catch (error) {
          console.error('Error reading Excel file:', error);
          toast.error("Error reading Excel file. Please make sure it's a valid Excel file.");
          setFile(null);
        }
      };
      reader.readAsArrayBuffer(selectedFile);
    }
  };

  // Function to upload the Excel file to the server
  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a file to upload");
      return;
    }

    setUploading(true);

    try {
      // Read the file content
      const reader = new FileReader();
      
      reader.onload = async (evt) => {
        try {
          const data = new Uint8Array(evt.target?.result as ArrayBuffer);
          const workbook = XLSX.read(data, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          
          // Process and send data to the server
          const axios = useAxios;
          const response = await axios.post('/candidate/bulk-upload', {
            candidates: jsonData
          }, {
            headers: {
              'Content-Type': 'application/json'
            }
          });
          
          // Show success message with notification stats
          const notificationStats = response.data.notification_stats || { sent: 0, total: 0 };
          const resumeMessage = notificationStats.total > 0 
            ? `${notificationStats.sent} out of ${notificationStats.total} candidates without resumes were sent WhatsApp messages.` 
            : '';
          
          toast.success(`Successfully uploaded ${jsonData.length} candidates! ${resumeMessage}`);
          setFile(null);
          setShowPreview(false);
          setPreview([]);
        } catch (error: any) {
          console.error('Error uploading candidates:', error);
          toast.error(error.response?.data?.message || "Error uploading candidates");
        } finally {
          setUploading(false);
        }
      };
      
      reader.readAsArrayBuffer(file);
    } catch (error) {
      console.error('Error:', error);
      toast.error("An error occurred during the upload process");
      setUploading(false);
    }
  };

  return (
    <>
      <HeadMain title="Bulk Upload Candidates" description={""} />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss={false}
        draggable
        pauseOnHover
        theme="dark"
      />
      
      <div className="mb-6">
        <BreadcrumbDashboard title="Bulk Upload Candidates" />
      </div>
      
      <Paper className="p-6 dark:bg-gray-800">
        <Typography variant="h5" className="mb-6 dark:text-white">
          Upload Candidates via Excel
        </Typography>
        
        <Alert severity="info" className="mb-6">
          Download the template, fill in your candidate details, and upload the completed file.
          Required fields: candidate_name, email, phone_number, department, has_resume.
          <br />
          {/* <strong>Note:</strong> Candidates with has_resume=FALSE will automatically receive a WhatsApp message asking them to upload their resume.
          <br />
          <strong>Important:</strong> Please ensure phone numbers include the country code (e.g., +1234567890) for WhatsApp notifications to work correctly. */}
        </Alert>
        
        <Box className="flex flex-col md:flex-row gap-4 mb-8">
          <Button
            variant="outlined"
            startIcon={<MdFileDownload />}
            onClick={handleDownloadTemplate}
            className="dark:text-white dark:border-white"
          >
            Download Template
          </Button>
          
          <Box className="flex-1">
            <input
              type="file"
              id="excel-upload"
              accept=".xlsx, .xls"
              onChange={handleFileChange}
              className="hidden"
              disabled={uploading}
            />
            <label htmlFor="excel-upload">
              <Button
                component="span"
                variant="contained"
                startIcon={<MdCloudUpload />}
                disabled={uploading}
                className="w-full"
              >
                {uploading ? "Uploading..." : "Select Excel File"}
              </Button>
            </label>
          </Box>
          
          <Button
            variant="contained"
            color="success"
            disabled={!file || uploading}
            onClick={handleUpload}
          >
            {uploading ? "Processing..." : "Upload Candidates"}
          </Button>
        </Box>
        
        {file && (
          <Alert severity="success" className="mb-4">
            Selected file: {file.name}
          </Alert>
        )}
        
        {showPreview && preview.length > 0 && (
          <div className="mt-8">
            <Typography variant="h6" className="mb-2 dark:text-white">
              Data Preview (First 5 rows)
            </Typography>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-gray-700 rounded-lg">
                <thead>
                  <tr>
                    {Object.keys(preview[0]).map((key) => (
                      <th key={key} className="py-2 px-4 text-left dark:text-white">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.map((row, index) => (
                    <tr key={index} className="border-t">
                      {Object.keys(preview[0]).map((key) => (
                        <td key={`${index}-${key}`} className="py-2 px-4 dark:text-white">
                          {String(row[key] || "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Paper>
    </>
  );
};

export default BulkUploadPage; 