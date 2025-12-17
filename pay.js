
// Adyen 加密占位脚本：提供与 Python 侧 execjs 调用一致的接口。
// 注意：仅用于本地调试，真实场景应替换为 Adyen 官方加密库。

function _enc(val, generationtime) {
  // 简单双向“加密”占位：Base64 + 前缀；不安全，仅用于跑通流程
  const s = String(val) + '|' + String(generationtime);
  return 'enc_' + Buffer.from(s).toString('base64');
}

function ccnum_encrypt(number, generationtime) {
  return _enc(number, generationtime);
}
function expm_encrypt(month, generationtime) {
  return _enc(month, generationtime);
}
function expy_encrypt(year, generationtime) {
  return _enc(year, generationtime);
}
function cvv_encrypt(cvv, generationtime) {
  return _enc(cvv, generationtime);
}

module.exports = { ccnum_encrypt, expm_encrypt, expy_encrypt, cvv_encrypt };
