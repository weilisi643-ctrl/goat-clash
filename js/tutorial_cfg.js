// 新手教学战配置（design/08）：文案 / 奖励 / 对手 stageCfg 模板。文案在此登记，tools/gen_font_subset.py 会扫描本文件生成字体子集。
module.exports = {
  tips: { 1: '两只羊同时跳起，用羊角顶对方！', 2: '对手的角度写在上面，选一个不被它克制的角度', 3: '指针走到金色区时点「起跳顶角」', 4: '完美起跳就是这一下，越准越有力！' },
  miss: '差一点，再试试看准金色区', win: '赢了！去挑选你的羊毛和羊角吧', lose: '没关系，看准金色区再来一次',
  reward: { color: '#CDB8F0', name: '薰衣草紫' }, // 奖励色：单一配置值（浅薰衣草）
  opponent: { id: 'tutorial', name: '小白羊', look: { wool: 'fluffy', woolColor: '#FFFFFF', horn: 'curl' },
    stage: { angleReveal: 'public', ai: { timingHit: 0, powBonus: 0, hpBonus: 0, readAcc: 0, counterPick: 0 }, clueLv: 1, playerHorn: 'curl', bestOf: 3 } },
  labels: { skip: '跳过', settings: '设置', replay: '重玩教学', back: '返回', toCustom: '去换装', again: '再来一局', home: '回主页', perfect: '完美起跳 ', times: ' 次', got: ' · 获得羊毛色「', gotEnd: '」', perfectPop: '完美！', score: '本场比分 · ', win: '胜 利 !', lose: '再接再厉' }
};
