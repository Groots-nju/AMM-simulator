/**
 * 本文件定义了关于用户请求的相关api
 */

// 从utils/http.js中导入instance，并命名为http（可以视为本文件中的http就是utils/http.js文件中的instance）
import http from '../utils/http';


// 用户相关的具体api如下
// NOTE: 命名规范：如果api设计网络请求（通常都是），那么应当以$开头，这提示api的使用者，这样的api可能会涉及异步处理，
// 如下例定义了一个名为“$userLogin”的api，它是一个异步函数（因为加上了async），所以使用者必须通过await关键字还同步等待其结果
/**
 * @param {object} loginData 用户进行登录所需的数据，包含username字段和password字段
 */
export const $userLogin = async (loginData) => {
    // axios.post(url, data)，data是一个object类型，即请求体，这里的url之前加上/api是因为跨域问题（后端其实没有/api）
    // 通过await关键字等待网络请求结果，结果放在res中
    const res = await http.post("/api/user/login", loginData);
    return res;
}

/**
 * 用户信息修改
 * @param {object} modifyData 包含待修改的字段，可为部分字段，如 { nickname: "新昵称" }
 * @returns {Promise<any>}
 */
export const $userModify = async (modifyData) => {
    const res = await http.put("/api/user/modify", modifyData);  // 注意是PUT方法
    return res;
};

/**
 * 用户登出（也就是接口文档写的注销）
 */
export const $userLogout = async () => {
    // 实际上由于拦截器的存在，每个非200的代码都会导致await报异常，所以严格意义上每个await都需要使用try-catch来包含，
    // 但是由于前端在用户端，只要该异常行为对后端服务器没有影响，一般也不需要使用try-catch（为了开发方便），当然用上最好
    try {
        await http.post("/api/user/logout");
    } catch (error) { // 这里简单处理，只是打印错误信息
        console.error("注销失败", error);
    } finally {
        // 保证一定执行（想一想，为什么在该函数中只需要将token和user_info清空，刷新页面的逻辑需要交给调用方）
        // 清空本地存储中的token
        const token = localStorage.getItem("jwt_token");
        if (token) {
            localStorage.removeItem("jwt_token");
        }
        // 清空本地存储中的用户信息
        const userInfo = localStorage.getItem("user_info");
        if (userInfo) {
            localStorage.removeItem("user_info");
        }
    }
}

/**
 * 用户注册，根据传入的用户数据，注册一个新用户
 * @param {object} registerData 
 */
export const $userRegister = async (registerData) => {
    // 对于这种不需要返回结果的请求，我们只需要根据状态码得到本次请求的结果，
    // 那么可以利用拦截器的异常处理机制来操作。那么该函数就只需要如下的一行代码：
    // 如果成功，调用方正常执行；如果失败，调用方会接受到异常（以此作为注册失败的信号）
    await http.post("/api/user/register", registerData);
}

/**
 * 获取用户信息,并加以展示
 * @param {object} userProfileData
 */
export const $getUserProfile = async (userProfileData) => {
    // 这里的userProfileData是一个对象，包含了用户的id和token
    let res = null; // 在函数作用域中声明
    try{ 
        res=await http.get("/api/user/query", userProfileData);
    } catch (error) { // 这里简单处理，只是打印错误信息
        console.error("获取用户信息失败", error);
    } finally {
        // 保证一定执行
        return res;
    }
}

