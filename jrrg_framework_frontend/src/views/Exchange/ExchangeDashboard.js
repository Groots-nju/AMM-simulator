import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Empty,
  Form,
  Input,
  message,
  Progress,
  Row,
  Select,
  Slider,
  Space,
  Statistic,
  Table,
  Tabs,
  Tag,
  Typography,
} from 'antd';
import {
  ApiOutlined,
  BarChartOutlined,
  ReloadOutlined,
  SwapOutlined,
  WalletOutlined,
} from '@ant-design/icons';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import {
  $addLiquidity,
  $executeSwap,
  $faucet,
  $getHistory,
  $getPools,
  $getPositions,
  $getTokens,
  $getWallet,
  $quoteSwap,
  $removeLiquidity,
  $resetSimulation,
} from '../../api/exchangeApi';
import './ExchangeDashboard.scss';

const { Text, Title } = Typography;

const sectionRoutes = {
  overview: '/exchange',
  swap: '/exchange/swap',
  liquidity: '/exchange/liquidity',
  wallet: '/exchange/wallet',
  history: '/exchange/history',
};

const eventColor = {
  swap: 'blue',
  faucet: 'green',
  add_liquidity: 'cyan',
  remove_liquidity: 'orange',
  reset: 'red',
};

const num = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const money = (value, digits = 2) => num(value).toLocaleString('en-US', {
  minimumFractionDigits: digits,
  maximumFractionDigits: digits,
});

const amount = (value, digits = 6) => num(value).toLocaleString('en-US', {
  maximumFractionDigits: digits,
});

const pct = (value, digits = 2) => `${(num(value) * 100).toFixed(digits)}%`;

const asArray = (value) => (Array.isArray(value) ? value : []);

const eventLabel = (type) => ({
  swap: 'Swap',
  faucet: 'Faucet',
  add_liquidity: 'Add LP',
  remove_liquidity: 'Remove LP',
  reset: 'Reset',
}[type] || type);

function ExchangeDashboard({ section = 'overview' }) {
  const navigate = useNavigate();
  const [tokens, setTokens] = useState([]);
  const [pools, setPools] = useState([]);
  const [wallet, setWallet] = useState([]);
  const [positions, setPositions] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedPoolId, setSelectedPoolId] = useState('');
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [quote, setQuote] = useState(null);
  const [swapForm, setSwapForm] = useState({ token_in_symbol: '', amount_in: '', slippage: '0.005' });
  const [liquidityForm, setLiquidityForm] = useState({ amount0: '', amount1: '', removeFraction: 0.25 });

  const selectedPool = useMemo(
    () => pools.find((pool) => pool.id === selectedPoolId) || pools[0],
    [pools, selectedPoolId],
  );

  const walletMap = useMemo(
    () => wallet.reduce((result, item) => ({ ...result, [item.symbol]: item.balance }), {}),
    [wallet],
  );

  const totalTvl = pools.reduce((sum, pool) => sum + num(pool.tvl_usdc), 0);
  const totalFees = pools.reduce((sum, pool) => sum + num(pool.cumulative_fee1), 0);

  const loadExchange = useCallback(async () => {
    setLoading(true);
    try {
      const [tokenData, poolData, walletData, positionData, historyData] = await Promise.all([
        $getTokens(),
        $getPools(),
        $getWallet(),
        $getPositions(),
        $getHistory(),
      ]);
      const normalizedTokens = asArray(tokenData);
      const normalizedPools = asArray(poolData);
      const normalizedWallet = asArray(walletData);
      const normalizedPositions = asArray(positionData);
      const normalizedHistory = asArray(historyData);
      setTokens(normalizedTokens);
      setPools(normalizedPools);
      setWallet(normalizedWallet);
      setPositions(normalizedPositions);
      setHistory(normalizedHistory);
      if ((!selectedPoolId || !normalizedPools.some((pool) => pool.id === selectedPoolId)) && normalizedPools.length > 0) {
        setSelectedPoolId(normalizedPools[0].id);
        setSwapForm((current) => ({ ...current, token_in_symbol: normalizedPools[0].token0.symbol }));
      }
    } catch (error) {
      message.error(error.message || '交易所数据加载失败');
    } finally {
      setLoading(false);
    }
  }, [selectedPoolId]);

  useEffect(() => {
    loadExchange();
  }, [loadExchange]);

  useEffect(() => {
    if (!selectedPool) return;
    setSwapForm((current) => ({
      ...current,
      token_in_symbol: current.token_in_symbol || selectedPool.token0.symbol,
    }));
  }, [selectedPool]);

  const changePool = (poolId) => {
    const pool = pools.find((item) => item.id === poolId);
    setSelectedPoolId(poolId);
    setQuote(null);
    setLiquidityForm({ amount0: '', amount1: '', removeFraction: 0.25 });
    setSwapForm({ token_in_symbol: pool?.token0.symbol || '', amount_in: '', slippage: '0.005' });
  };

  const refreshAfterAction = async () => {
    setQuote(null);
    await loadExchange();
  };

  const handleQuote = async () => {
    if (!selectedPool || !swapForm.amount_in || !swapForm.token_in_symbol) {
      message.warning('请选择交易池并输入交易数量');
      return;
    }
    setActionLoading(true);
    try {
      const data = await $quoteSwap({
        pool_id: selectedPool.id,
        token_in_symbol: swapForm.token_in_symbol,
        amount_in: swapForm.amount_in,
      });
      setQuote(data);
    } catch (error) {
      setQuote(null);
      message.error(error.message || '报价失败');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSwap = async () => {
    if (!quote || !selectedPool) {
      message.warning('请先获取报价');
      return;
    }
    const minOut = num(quote.amount_out) * (1 - num(swapForm.slippage));
    setActionLoading(true);
    try {
      await $executeSwap({
        pool_id: selectedPool.id,
        token_in_symbol: swapForm.token_in_symbol,
        amount_in: swapForm.amount_in,
        min_amount_out: String(minOut),
      });
      message.success('Swap 成交');
      await refreshAfterAction();
    } catch (error) {
      message.error(error.message || 'Swap 失败');
    } finally {
      setActionLoading(false);
    }
  };

  const fillProportionalAmount1 = (amount0Value) => {
    if (!selectedPool) return;
    const amount0 = num(amount0Value);
    const ratio = num(selectedPool.reserve1) / Math.max(num(selectedPool.reserve0), 1e-12);
    setLiquidityForm((current) => ({
      ...current,
      amount0: amount0Value,
      amount1: amount0 > 0 ? String(amount0 * ratio) : '',
    }));
  };

  const handleAddLiquidity = async () => {
    if (!selectedPool || !liquidityForm.amount0 || !liquidityForm.amount1) {
      message.warning('请输入两侧资产数量');
      return;
    }
    setActionLoading(true);
    try {
      await $addLiquidity({
        pool_id: selectedPool.id,
        amount0: liquidityForm.amount0,
        amount1: liquidityForm.amount1,
      });
      message.success('流动性添加成功');
      await refreshAfterAction();
    } catch (error) {
      message.error(error.message || '添加流动性失败');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRemoveLiquidity = async () => {
    if (!selectedPool) return;
    setActionLoading(true);
    try {
      await $removeLiquidity({
        pool_id: selectedPool.id,
        share_fraction: String(liquidityForm.removeFraction),
      });
      message.success('流动性已移除');
      await refreshAfterAction();
    } catch (error) {
      message.error(error.message || '移除流动性失败');
    } finally {
      setActionLoading(false);
    }
  };

  const handleFaucet = async () => {
    setActionLoading(true);
    try {
      await $faucet();
      message.success('已领取模拟资产');
      await refreshAfterAction();
    } catch (error) {
      message.error(error.message || '领取模拟资产失败');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReset = async () => {
    setActionLoading(true);
    try {
      await $resetSimulation();
      message.success('仿真已重置，并发放初始模拟资产');
      await refreshAfterAction();
    } catch (error) {
      message.error(error.message || '重置失败');
    } finally {
      setActionLoading(false);
    }
  };

  const poolOptions = pools.map((pool) => ({
    label: pool.name,
    value: pool.id,
  }));
  const selectedPoolPosition = positions.find((position) => position.pool.id === selectedPool?.id);
  const tokenOptions = selectedPool
    ? [
        { label: selectedPool.token0.symbol, value: selectedPool.token0.symbol },
        { label: selectedPool.token1.symbol, value: selectedPool.token1.symbol },
      ]
    : [];

  const tabs = [
    {
      key: 'overview',
      label: '总览',
      children: (
        <OverviewPanel
          pools={pools}
          history={history}
          totalTvl={totalTvl}
          totalFees={totalFees}
          loading={loading}
          onPoolOpen={(poolId) => {
            changePool(poolId);
            navigate('/exchange/swap');
          }}
        />
      ),
    },
    {
      key: 'swap',
      label: 'Swap',
      children: (
        <SwapPanel
          selectedPool={selectedPool}
          poolOptions={poolOptions}
          tokenOptions={tokenOptions}
          walletMap={walletMap}
          quote={quote}
          swapForm={swapForm}
          loading={actionLoading}
          onPoolChange={changePool}
          onFormChange={setSwapForm}
          onQuote={handleQuote}
          onSwap={handleSwap}
        />
      ),
    },
    {
      key: 'liquidity',
      label: '流动性',
      children: (
        <LiquidityPanel
          selectedPool={selectedPool}
          selectedPoolPosition={selectedPoolPosition}
          poolOptions={poolOptions}
          walletMap={walletMap}
          liquidityForm={liquidityForm}
          loading={actionLoading}
          onPoolChange={changePool}
          onAmount0Change={fillProportionalAmount1}
          onFormChange={setLiquidityForm}
          onAdd={handleAddLiquidity}
          onRemove={handleRemoveLiquidity}
        />
      ),
    },
    {
      key: 'wallet',
      label: '钱包',
      children: (
        <WalletPanel
          tokens={tokens}
          wallet={wallet}
          loading={actionLoading}
          onFaucet={handleFaucet}
          onReset={handleReset}
        />
      ),
    },
    {
      key: 'history',
      label: '历史',
      children: <HistoryPanel history={history} loading={loading} />,
    },
  ];

  return (
    <div className="dex-page">
      <section className="dex-page-head">
        <div>
          <Text className="eyebrow">AMM Decentralized Exchange</Text>
          <Title level={2}>本地交易所仿真工作台</Title>
          <Text className="muted-text">Swap、LP、钱包和事件历史全部由 Flask 后端的本地 AMM 状态推进。</Text>
        </div>
        <Space wrap>
          <Button icon={<ReloadOutlined />} onClick={loadExchange} loading={loading}>刷新</Button>
          <Button type="primary" icon={<WalletOutlined />} onClick={handleFaucet} loading={actionLoading}>领取模拟资产</Button>
        </Space>
      </section>

      <Alert
        className="simulation-alert"
        type="info"
        showIcon
        message="本系统只运行本地仿真资产，不连接真实钱包、链上 RPC 或真实行情。"
      />

      <Tabs
        className="dex-tabs"
        activeKey={section}
        onChange={(key) => navigate(sectionRoutes[key])}
        items={tabs}
      />
    </div>
  );
}

function OverviewPanel({ pools, history, totalTvl, totalFees, loading, onPoolOpen }) {
  const chartData = pools.map((pool) => ({
    name: pool.token0.symbol,
    tvl: Number(pool.tvl_usdc),
    price: Number(pool.spot_price_token1_per_token0),
  }));

  const poolColumns = [
    { title: '池子', dataIndex: 'name', key: 'name', render: (_, row) => <strong>{row.name}</strong> },
    { title: '价格', dataIndex: 'spot_price_token1_per_token0', render: (value, row) => `${money(value, 2)} ${row.token1.symbol}` },
    { title: 'TVL', dataIndex: 'tvl_usdc', render: (value) => `$${money(value, 2)}` },
    { title: '储备', key: 'reserve', render: (_, row) => `${amount(row.reserve0, 2)} ${row.token0.symbol} / ${amount(row.reserve1, 2)} ${row.token1.symbol}` },
    { title: '累计手续费', key: 'fees', render: (_, row) => `${amount(row.cumulative_fee0, 4)} ${row.token0.symbol} / ${amount(row.cumulative_fee1, 2)} ${row.token1.symbol}` },
    { title: '操作', key: 'action', render: (_, row) => <Button size="small" onClick={() => onPoolOpen(row.id)}>交易</Button> },
  ];

  return (
    <div className="panel-stack">
      <Row gutter={[14, 14]}>
        <Col xs={24} md={8}>
          <Card className="metric-card">
            <Statistic title="总 TVL" value={totalTvl} precision={2} prefix="$" />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="metric-card">
            <Statistic title="活跃池子" value={pools.length} suffix="Pools" />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="metric-card">
            <Statistic title="USDC 手续费累计" value={totalFees} precision={2} prefix="$" />
          </Card>
        </Col>
      </Row>

      <Row gutter={[14, 14]}>
        <Col xs={24} lg={10}>
          <Card title="池子 TVL 分布" className="dex-card">
            <div className="chart-box">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${money(value, 2)}`} />
                  <Bar dataKey="tvl" fill="#12a87d" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={14}>
          <Card title="交易池" className="dex-card">
            <Table
              rowKey="id"
              dataSource={pools}
              columns={poolColumns}
              pagination={false}
              loading={loading}
              size="middle"
            />
          </Card>
        </Col>
      </Row>

      <Card title="最近事件" className="dex-card">
        <HistoryTable history={history.slice(0, 8)} loading={loading} compact />
      </Card>
    </div>
  );
}

function SwapPanel({ selectedPool, poolOptions, tokenOptions, walletMap, quote, swapForm, loading, onPoolChange, onFormChange, onQuote, onSwap }) {
  const outputSymbol = quote?.token_out_symbol || (selectedPool?.token1.symbol || '');
  const inputBalance = walletMap[swapForm.token_in_symbol] || '0';
  const minOut = quote ? Number(quote.amount_out) * (1 - Number(swapForm.slippage || 0)) : 0;

  return (
    <Row gutter={[14, 14]}>
      <Col xs={24} lg={10}>
        <Card title="Swap 交易" className="dex-card">
          <Form layout="vertical">
            <Form.Item label="交易池">
              <Select value={selectedPool?.id} options={poolOptions} onChange={onPoolChange} />
            </Form.Item>
            <Form.Item label="输入资产">
              <Select
                value={swapForm.token_in_symbol}
                options={tokenOptions}
                onChange={(value) => {
                  onFormChange((current) => ({ ...current, token_in_symbol: value }));
                }}
              />
              <Text className="form-note">余额：{amount(inputBalance, 6)} {swapForm.token_in_symbol}</Text>
            </Form.Item>
            <Form.Item label="输入数量">
              <Input
                value={swapForm.amount_in}
                onChange={(event) => onFormChange((current) => ({ ...current, amount_in: event.target.value }))}
                placeholder="0.0"
              />
            </Form.Item>
            <Form.Item label="滑点保护">
              <Select
                value={swapForm.slippage}
                onChange={(value) => onFormChange((current) => ({ ...current, slippage: value }))}
                options={[
                  { label: '0.1%', value: '0.001' },
                  { label: '0.5%', value: '0.005' },
                  { label: '1.0%', value: '0.01' },
                ]}
              />
            </Form.Item>
            <Space className="action-row">
              <Button onClick={onQuote} loading={loading} icon={<BarChartOutlined />}>获取报价</Button>
              <Button type="primary" onClick={onSwap} loading={loading} icon={<SwapOutlined />} disabled={!quote}>执行 Swap</Button>
            </Space>
          </Form>
        </Card>
      </Col>
      <Col xs={24} lg={14}>
        <Card title="报价与价格影响" className="dex-card">
          {quote ? (
            <div className="quote-grid">
              <Metric label="预计获得" value={`${amount(quote.amount_out, 6)} ${outputSymbol}`} />
              <Metric label="最小获得" value={`${amount(minOut, 6)} ${outputSymbol}`} />
              <Metric label="手续费" value={`${amount(quote.fee_amount, 6)} ${quote.token_in_symbol}`} />
              <Metric label="价格影响" value={pct(quote.price_impact)} tone={Number(quote.price_impact) > 0.05 ? 'danger' : 'default'} />
              <Metric label="成交价格" value={amount(quote.execution_price, 8)} />
              <Metric label="成交后池子价格" value={`${money(quote.post_price_token1_per_token0, 4)} ${selectedPool?.token1.symbol}`} />
            </div>
          ) : (
            <Empty description="输入数量后获取 AMM 报价" />
          )}
          <Divider />
          <PoolSnapshot pool={selectedPool} />
        </Card>
      </Col>
    </Row>
  );
}

function LiquidityPanel({ selectedPool, selectedPoolPosition, poolOptions, walletMap, liquidityForm, loading, onPoolChange, onAmount0Change, onFormChange, onAdd, onRemove }) {
  const hasPosition = selectedPoolPosition && Number(selectedPoolPosition.lp_shares) > 0;
  return (
    <Row gutter={[14, 14]}>
      <Col xs={24} lg={10}>
        <Card title="添加流动性" className="dex-card">
          <Form layout="vertical">
            <Form.Item label="交易池">
              <Select value={selectedPool?.id} options={poolOptions} onChange={onPoolChange} />
            </Form.Item>
            <Form.Item label={`${selectedPool?.token0.symbol || 'Token0'} 数量`}>
              <Input
                value={liquidityForm.amount0}
                onChange={(event) => onAmount0Change(event.target.value)}
                placeholder="0.0"
              />
              <Text className="form-note">余额：{amount(walletMap[selectedPool?.token0.symbol] || 0, 6)} {selectedPool?.token0.symbol}</Text>
            </Form.Item>
            <Form.Item label={`${selectedPool?.token1.symbol || 'Token1'} 数量`}>
              <Input
                value={liquidityForm.amount1}
                onChange={(event) => onFormChange((current) => ({ ...current, amount1: event.target.value }))}
                placeholder="按池子比例自动估算"
              />
              <Text className="form-note">余额：{amount(walletMap[selectedPool?.token1.symbol] || 0, 6)} {selectedPool?.token1.symbol}</Text>
            </Form.Item>
            <Button type="primary" block onClick={onAdd} loading={loading} icon={<ApiOutlined />}>添加 LP</Button>
          </Form>
        </Card>
      </Col>
      <Col xs={24} lg={14}>
        <Card title="我的 LP 持仓" className="dex-card">
          {hasPosition ? (
            <>
              <div className="quote-grid">
                <Metric label="LP Shares" value={amount(selectedPoolPosition.lp_shares, 6)} />
                <Metric label="池子占比" value={pct(selectedPoolPosition.pool_share, 4)} />
                <Metric label="底层资产" value={`${amount(selectedPoolPosition.underlying0, 4)} ${selectedPool?.token0.symbol} / ${amount(selectedPoolPosition.underlying1, 2)} ${selectedPool?.token1.symbol}`} />
                <Metric label="当前价值" value={`$${money(selectedPoolPosition.current_value_usdc, 2)}`} />
                <Metric label="HODL 对比" value={`$${money(selectedPoolPosition.hodl_value_usdc, 2)}`} />
                <Metric label="IL 预估" value={pct(selectedPoolPosition.impermanent_loss_pct)} tone={Number(selectedPoolPosition.impermanent_loss_pct) < 0 ? 'danger' : 'default'} />
              </div>
              <Divider />
              <Text strong>撤出比例</Text>
              <Slider
                min={0.05}
                max={1}
                step={0.05}
                value={liquidityForm.removeFraction}
                onChange={(value) => onFormChange((current) => ({ ...current, removeFraction: value }))}
              />
              <Button danger onClick={onRemove} loading={loading}>移除 {pct(liquidityForm.removeFraction, 0)} LP</Button>
            </>
          ) : (
            <Empty description="当前交易池暂无 LP 持仓" />
          )}
        </Card>
      </Col>
    </Row>
  );
}

function WalletPanel({ tokens, wallet, loading, onFaucet, onReset }) {
  const rows = tokens.map((token) => ({
    ...token,
    balance: wallet.find((item) => item.symbol === token.symbol)?.balance || '0',
  }));
  return (
    <Card title="模拟钱包" className="dex-card">
      <div className="wallet-actions">
        <Alert type="warning" showIcon message="Faucet 只发放本地模拟资产，可重复领取用于演示。" />
        <Space wrap>
          <Button type="primary" onClick={onFaucet} loading={loading} icon={<WalletOutlined />}>领取默认资产</Button>
          <Button danger onClick={onReset} loading={loading} icon={<ReloadOutlined />}>重置仿真</Button>
        </Space>
      </div>
      <Table
        rowKey="symbol"
        dataSource={rows}
        pagination={false}
        columns={[
          { title: '资产', dataIndex: 'symbol', render: (value, row) => <strong>{value} · {row.name}</strong> },
          { title: '余额', dataIndex: 'balance', render: (value) => amount(value, 6) },
          { title: '精度', dataIndex: 'decimals' },
        ]}
      />
    </Card>
  );
}

function HistoryPanel({ history, loading }) {
  return (
    <Card title="交易历史" className="dex-card">
      <HistoryTable history={history} loading={loading} />
    </Card>
  );
}

function HistoryTable({ history, loading, compact = false }) {
  return (
    <Table
      rowKey="id"
      dataSource={history}
      loading={loading}
      pagination={compact ? false : { pageSize: 12 }}
      columns={[
        { title: '类型', dataIndex: 'event_type', render: (value) => <Tag color={eventColor[value] || 'default'}>{eventLabel(value)}</Tag> },
        { title: '摘要', dataIndex: 'summary' },
        { title: '池子', dataIndex: 'pool_id', render: (value) => value || '-' },
        { title: '时间', dataIndex: 'created_at', render: (value) => new Date(value).toLocaleString() },
      ]}
    />
  );
}

function PoolSnapshot({ pool }) {
  if (!pool) return null;
  return (
    <div className="pool-snapshot">
      <div>
        <span>池子价格</span>
        <strong>{money(pool.spot_price_token1_per_token0, 4)} {pool.token1.symbol}/{pool.token0.symbol}</strong>
      </div>
      <div>
        <span>储备深度</span>
        <strong>{amount(pool.reserve0, 2)} {pool.token0.symbol} / {amount(pool.reserve1, 2)} {pool.token1.symbol}</strong>
      </div>
      <div>
        <span>手续费率</span>
        <strong>{pct(pool.fee_rate)}</strong>
      </div>
      <Progress percent={Math.min(100, Math.round(num(pool.tvl_usdc) / 100000))} showInfo={false} />
    </div>
  );
}

function Metric({ label, value, tone = 'default' }) {
  return (
    <div className={`quote-metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default ExchangeDashboard;
