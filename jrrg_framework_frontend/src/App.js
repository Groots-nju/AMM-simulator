import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

// 导入页面组件
import Login from './views/Login/Login';
import Index from './views/Index/Index';
import NotFound from './views/NotFound/NotFound';
import Register from './views/Register/Register';
import UserProfile from './views/UserProfile/UserProfile'; 
import { useNavigate } from 'react-router-dom';
import { setNavigate } from './utils/http';
import RequierAuth from './components/RequireAuth/RequireAuth';
import Modify from "./views/Modify/Modify";
import ExchangeDashboard from './views/Exchange/ExchangeDashboard';


// NOTE 由于使用了useNavigate，所以必须单独定义一个页面（AppRoutes），你可以理解为固定写法
function AppRoutes() {
  // 为请求拦截器设置navigate
  const navigate = useNavigate();
  setNavigate(navigate);
  // 使用Routes定义多个不同的路由
  return (
    <Routes>

      {/* 使用Route定义某一个路由，如下是定义了当访问/login路径时，路由到Login页面 */}
      <Route path='/login' element={<Login />} />
      <Route path='/register' element={<Register />} />

      {/* 选择在App.js中统一设置路由，这样一来当其他页面想要使用该路由时，只要在相应位置使用<Outlet />代替即可 */}
      <Route path='/' element={<RequierAuth><Index /></RequierAuth>} >
        <Route index element={<Navigate to="/exchange" replace />} />
        <Route path="/home" element={<Navigate to="/exchange" replace />} />
        <Route path="/exchange" element={<ExchangeDashboard section="overview" />} />
        <Route path="/exchange/swap" element={<ExchangeDashboard section="swap" />} />
        <Route path="/exchange/liquidity" element={<ExchangeDashboard section="liquidity" />} />
        <Route path="/exchange/wallet" element={<ExchangeDashboard section="wallet" />} />
        <Route path="/exchange/history" element={<ExchangeDashboard section="history" />} />
        <Route path="/profile" element={<UserProfile />} />
        <Route path="profile/edit" element={<Modify />} />
      </Route>

      {/* 通常还需要统一设置一个404页面，在react-router-dom中，设置path="*"表示匹配所有未被定义的路由 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}


// 主程序
function App() {
  return (
    <div>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </div>
  );
}

export default App;
