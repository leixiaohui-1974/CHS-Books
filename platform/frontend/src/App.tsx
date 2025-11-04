/**
 * 应用主入口
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import LearningSession from './pages/LearningSession';
import './App.css';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/session" replace />} />
          <Route path="/session" element={<LearningSession />} />
          {/* 未来可以添加更多路由 */}
        </Routes>
      </Router>
    </ConfigProvider>
  );
};

export default App;
