import http from '../utils/http';

const unwrap = (res) => {
  if (!res || res.code !== 0) {
    throw new Error(res?.message || '交易所接口请求失败');
  }
  return res.data;
};

export const $getTokens = async () => unwrap(await http.get('/api/exchange/tokens'));
export const $getPools = async () => unwrap(await http.get('/api/exchange/pools'));
export const $getPool = async (poolId) => unwrap(await http.get(`/api/exchange/pools/${poolId}`));
export const $getWallet = async () => unwrap(await http.get('/api/exchange/wallet'));
export const $getPositions = async () => unwrap(await http.get('/api/exchange/positions'));
export const $getHistory = async () => unwrap(await http.get('/api/exchange/history'));
export const $faucet = async (amounts) => unwrap(await http.post('/api/exchange/faucet', amounts ? { amounts } : {}));
export const $quoteSwap = async (payload) => unwrap(await http.post('/api/exchange/swap/quote', payload));
export const $executeSwap = async (payload) => unwrap(await http.post('/api/exchange/swap', payload));
export const $addLiquidity = async (payload) => unwrap(await http.post('/api/exchange/liquidity/add', payload));
export const $removeLiquidity = async (payload) => unwrap(await http.post('/api/exchange/liquidity/remove', payload));
export const $resetSimulation = async () => unwrap(await http.post('/api/exchange/simulation/reset'));
