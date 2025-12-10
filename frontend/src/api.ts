// src/api.ts
import axios from 'axios'

const http = axios.create({
  baseURL: 'http://127.0.0.1:8001', // 你的 uvicorn 后端端口
  timeout: 20000
})

/* ---------------------------
 * 文件选择页面 API
 * --------------------------- */
export const listFiles = () =>
  http.get('/files').then(res => res.data)

export const startAnalyze = (files: string[]) =>
  http.post('/jobs/start', { files }).then(res => res.data)

/* ---------------------------
 * 任务进度页面 API
 * --------------------------- */
export const getProgress = (jobId: string) =>
  http.get(`/jobs/${jobId}/progress`).then(res => res.data)

/* ---------------------------
 * Overview 总览数据
 * --------------------------- */
export const getOverview = (jobId: string) =>
  http.get(`/results/${jobId}/overview`).then(res => res.data)

/* ---------------------------
 * RackDetail 页面
 * --------------------------- */
export const getRackDetail = (jobId: string, rackId: number) =>
  http.get(`/results/${jobId}/rack/${rackId}`).then(res => res.data)

/* ---------------------------
 * CellDetail 页面
 * --------------------------- */
export const getCellDetail = (jobId: string, rackId: number, moduleId: number, cellId: number) =>
  http.get(`/results/${jobId}/rack/${rackId}/module/${moduleId}/cell/${cellId}`).then(res => res.data)

/* ---------------------------
 * 日志查看
 * --------------------------- */
export const getJobLog = (jobId: string) =>
  http.get(`/jobs/${jobId}/log`).then(res => res.data)

export default {
  listFiles,
  startAnalyze,
  getProgress,
  getOverview,
  getRackDetail,
  getCellDetail,
  getJobLog
}
