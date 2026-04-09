import request from "@/utils/request";

const API_PATH = "/common/file";

const FileAPI = {
  fileUpload(file: FormData) {
    return request<ApiResponse<UploadFilePath>>({
      url: `${API_PATH}/upload`,
      method: "post",
      params: file,
    });
  },

  fileDownload(file_path: string) {
    return request<Blob>({
      url: `${API_PATH}/download`,
      method: "post",
      params: file_path,
    });
  },
};

export default FileAPI;
