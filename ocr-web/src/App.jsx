import React, { useState, useRef } from 'react';
import axios from 'axios';
import { 
  UploadCloud, FileSpreadsheet, CheckCircle2, 
  AlertCircle, FileImage, Loader2, Download 
} from 'lucide-react';

// === 配置：后端地址 ===
const API_BASE = 'http://127.0.0.1:8000/api/v1';

function App() {
  // 1. 定义状态
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [data, setData] = useState(null); // 完整的后端响应数据
  const [items, setItems] = useState([]); // 表格行数据
  const fileInputRef = useRef(null);

  // 2. 处理文件选择
  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) processFile(selectedFile);
  };

  // 3. 处理拖拽上传
  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      processFile(droppedFile);
    }
  };

  // 4. 核心逻辑：上传并识别
  const processFile = async (file) => {
    setFile(file);
    setPreview(URL.createObjectURL(file));
    setLoading(true);
    setItems([]);
    setStatusMsg('正在上传图片...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // 阶段一：上传与OCR
      setStatusMsg('PaddleOCR 正在极速识别...');
      const response = await axios.post(`${API_BASE}/ocr/analyze`, formData);
      
      // 阶段二：处理结果
      setStatusMsg('AI 正在清洗数据...');
      const resData = response.data;
      
      if (resData.status === 'success') {
        setData(resData); // 保存完整数据用于导出
        setItems(resData.data.items || []);
      } else {
        alert(`识别失败: ${resData.message}`);
      }
    } catch (error) {
      console.error(error);
      alert('请求失败，请检查后端 Python 服务是否启动');
    } finally {
      setLoading(false);
    }
  };

  // 5. 导出 Excel
  const handleExport = async () => {
    if (!data) return;
    try {
      const response = await axios.post(`${API_BASE}/ocr/export-excel`, data, {
        responseType: 'blob' // 关键：告诉 axios 返回的是文件流
      });

      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // 解析文件名
      const contentDisposition = response.headers['content-disposition'];
      let fileName = `${file?.name.split('.')[0]}_识别结果.xlsx`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename\*=utf-8''(.+)/);
        if (match?.[1]) fileName = decodeURIComponent(match[1]);
      }
      
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('导出失败');
    }
  };

  // --- 辅助函数：判断数据状态 ---
  // 是否有差异
  const isDiff = (row) => {
    if (row.actual_count == null || row.system_stock == null) return false;
    // 提取数字进行比较
    const sys = parseFloat(String(row.system_stock).replace(/[^\d.]/g, ''));
    const act = parseFloat(String(row.actual_count).replace(/[^\d.]/g, ''));
    return !isNaN(sys) && !isNaN(act) && sys !== act;
  };

  // 获取文字颜色
  const getStatusClass = (row) => {
    if (row.actual_count == null) return 'text-yellow-600 italic bg-yellow-50'; // 漏填
    if (isDiff(row)) return 'text-red-600 font-bold bg-red-50'; // 差异
    return 'text-green-600 font-medium'; // 正常
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-700 flex flex-col font-sans">
      
      {/* === 顶部导航栏 === */}
      <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 shadow-sm z-20">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2 rounded-lg">
            <FileSpreadsheet size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-800">
              智能单据识别系统
            </h1>
            <p className="text-[10px] text-gray-400 -mt-1">Universal OCR Enterprise</p>
          </div>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium ml-2">
            在线版
          </span>
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <CheckCircle2 size={14} className="text-green-500" /> GPU 引擎就绪
          </span>
        </div>
      </header>

      {/* === 主内容区 === */}
      <main className="flex-1 p-6 overflow-hidden">
        <div className="max-w-7xl mx-auto h-full flex gap-6">
          
          {/* --- 左侧：上传区 --- */}
          <div className="w-1/3 flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
              <span className="font-semibold text-gray-700 flex items-center gap-2">
                <FileImage size={18} /> 原图预览
              </span>
              {file && <span className="text-xs text-gray-400 truncate max-w-[150px]">{file.name}</span>}
            </div>

            <div 
              className="flex-1 relative group cursor-pointer bg-slate-100 transition-colors hover:bg-slate-200"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
            >
              {/* 图片展示 */}
              {preview ? (
                <div className="w-full h-full p-4 flex items-center justify-center bg-gray-900/5">
                  <img src={preview} alt="Preview" className="max-w-full max-h-full object-contain shadow-lg" />
                </div>
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
                  <UploadCloud size={64} className="mb-4 text-gray-300 group-hover:text-blue-500 transition-colors" />
                  <p className="font-medium text-gray-500">点击或拖拽上传单据</p>
                  <p className="text-xs mt-2 opacity-60">支持 JPG, PNG 高清扫描件</p>
                </div>
              )}

              {/* Loading 遮罩 */}
              {loading && (
                <div className="absolute inset-0 bg-white/90 backdrop-blur-sm z-20 flex flex-col items-center justify-center">
                  <Loader2 size={40} className="text-blue-600 animate-spin mb-3" />
                  <p className="text-blue-600 font-medium animate-pulse">{statusMsg}</p>
                </div>
              )}
              
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="image/*" 
                onChange={handleFileSelect} 
              />
            </div>
          </div>

          {/* --- 右侧：结果区 --- */}
          <div className="w-2/3 flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
              <span className="font-semibold text-gray-700 flex items-center gap-2">
                <FileSpreadsheet size={18} /> 识别结果
                {items.length > 0 && (
                  <span className="bg-gray-200 text-gray-600 text-xs px-2 py-0.5 rounded-full">
                    {items.length} 条
                  </span>
                )}
              </span>
              
              <button 
                onClick={handleExport}
                disabled={!items.length || loading}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium transition-all shadow-sm
                  ${items.length 
                    ? 'bg-green-600 text-white hover:bg-green-700 hover:shadow' 
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
              >
                <Download size={16} /> 导出 Excel
              </button>
            </div>

            <div className="flex-1 overflow-auto relative">
              {items.length > 0 ? (
                <table className="w-full text-sm text-left border-collapse">
                  <thead className="text-xs text-gray-500 uppercase bg-gray-50 sticky top-0 z-10 shadow-sm">
                    <tr>
                      <th className="px-6 py-3 font-medium">商品名称</th>
                      <th className="px-4 py-3 font-medium">编码</th>
                      <th className="px-4 py-3 font-medium w-20">单位</th>
                      <th className="px-4 py-3 font-medium text-right">系统库存</th>
                      <th className="px-4 py-3 font-medium text-right">实盘数</th>
                      <th className="px-4 py-3 font-medium text-center w-24">状态</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {items.map((row, index) => (
                      <tr key={index} className="hover:bg-blue-50/50 transition-colors group">
                        <td className="px-6 py-3 font-medium text-gray-700">{row.name}</td>
                        <td className="px-4 py-3 text-gray-400 font-mono text-xs">
                          {row.code === 'DEFAULT' ? <span className="opacity-30">-</span> : row.code}
                        </td>
                        <td className="px-4 py-3 text-gray-500">{row.unit || '-'}</td>
                        <td className="px-4 py-3 text-right font-mono text-gray-600">
                          {row.system_stock ?? '-'}
                        </td>
                        
                        {/* 智能高亮单元格 */}
                        <td className={`px-4 py-3 text-right font-mono text-base ${getStatusClass(row)}`}>
                          {row.actual_count ?? '待查'}
                        </td>

                        <td className="px-4 py-3 text-center">
                          {row.actual_count == null ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                              <AlertCircle size={10} className="mr-1"/> 漏填
                            </span>
                          ) : isDiff(row) ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                              <AlertCircle size={10} className="mr-1"/> 差异
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                              <CheckCircle2 size={10} className="mr-1"/> 正常
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                /* 空状态 */
                <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-300">
                  <FileSpreadsheet size={64} className="mb-4 opacity-20" />
                  <p>暂无数据</p>
                  <p className="text-xs mt-2">请从左侧上传图片</p>
                </div>
              )}
            </div>

            {/* 底部统计栏 */}
            <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 text-xs text-gray-500 flex justify-between">
               <span>系统状态: 正常</span>
               <div className="flex gap-4">
                 <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-green-500 mr-1.5"></div> 账实相符</span>
                 <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-red-500 mr-1.5"></div> 库存差异</span>
                 <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-yellow-500 mr-1.5"></div> 数据缺失</span>
               </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;