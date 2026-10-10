# 30 秒引流宣传片 · 分镜脚本与 AI 生成提示词

> **定位**：氛围宣传片（引流）→ 承接 `assets/demo-video.mp4`（真实能力演示）
> **风格**：写实电影感 ｜ **时长**：30 秒 ｜ **画幅**：16:9 / 1920×1080 / 24 或 30fps
> **状态**：🟡 可拍摄（脚本定稿，参考图已产出）

---

## 0. 一句话概念

> **物理上只有一个人，但有一束「对话的光」证明他并不孤单。**

这条片子**不讲功能，只讲情绪**：前 16 秒把人拉进「深夜一个人的饭」这个共鸣现场，
后 14 秒才让他看见——原来有人记得他上次点了什么。

**产品能力交给 `assets/demo-video.mp4` 去证明**。两支片子是接力关系，不是重复关系。

### 情绪曲线

```
孤独感 ▁▂▃▄▅▆▇  转折 ↘  被接住 ▃▅▆▇█  收束 ▆▅
       镜1  镜2  镜3   镜4    镜5    镜6    镜7
```

---

## 1. 硬约束（先看这条，违反了整条片子作废）

| 类别 | 约束 | 原因 |
| --- | --- | --- |
| 商标 | **不出现任何品牌 Logo、金色拱门「M」、可读品牌文字、带商标的包装** | 合规红线（与 `BANNER.md` 同规则） |
| 品牌态度 | 不贬低、不讽刺、不与其他品牌对比 | 赛事规则「其他说明」 |
| 导向 | 不鼓吹多吃、不宣扬不健康饮食 | 同上 |
| 情绪 | **哀而不伤**。孤独可以有，凄苦不要有——不要出现醉汉、垃圾堆、雨夜痛哭这类符号 | 品牌调性 + 产品是「治愈」不是「卖惨」 |
| 人脸 | 建议**不出现清晰正脸**：只用背影、侧影、逆光、低头、手部与局部特写 | ① 与 `BANNER.md`「无人脸」规范一致；② **规避 AI 视频人脸崩坏**；③ 免肖像问题 |
| 一致性 | **不要试图让镜1和镜6是同一个人**。AI 站跨镜无法保持人物一致，所以刻意一个给背影、一个给侧脸，永远不出现可辨认正脸 | 这是设计选择，不是妥协 |

---

## 2. 全片节奏总表

| 镜 | 时间 | 时长 | 画面一句话 | 旁白 | 素材来源 |
| --- | --- | --- | --- | --- | --- |
| 1 | 00:00–00:03.5 | 3.5s | 深夜写字楼，一个背影走出旋转门 | —（留白） | AI 生成 · `REF-01` |
| 2 | 00:03.5–00:07 | 3.5s | 快餐店窗外，玻璃透出暖光，他推门进去 | 「晚上九点，又是一个人。」 | AI 生成 · `REF-02` |
| 3 | 00:07–00:12 | 5.0s | 餐盘特写缓推，对面椅子空着 | 「一个人吃饭，难的从来都不是饭。」/「是没人说话。」 | AI 生成 · `REF-03` |
| 4 | 00:12–00:16 | 4.0s | 手机在桌面亮起，琥珀光映出一小片 | — | AI 生成 · `REF-04` |
| 5 | 00:16–00:23 | 7.0s | **真实产品界面**三连（记忆 → 算价 → 订单卡） | 「所以我们做了个饭搭子。」/「它记得你上次点了什么，报价一分不差。」 | **真实截图** |
| 6 | 00:23–00:26.5 | 3.5s | 侧脸低头看屏幕，肩膀松下，微微笑 | 「帮你把单下好，陪你把这顿吃完。」 | AI 生成 · `REF-05` |
| 7 | 00:26.5–00:30 | 3.5s | 品牌卡：光团子 + 标题 + Slogan + CTA | 「一个人吃饭，但不孤单。」 | 代码渲染 · `REF-06` 为底 |

> ⏱ **前 3.5 秒完全没有旁白**，只有环境音。这不是浪费——是让观众先"进入"这个夜晚。

---

## 3. 逐镜详表

### 镜 1 · 深夜写字楼（3.5s）

- **首帧参考图**：`assets/video-refs/REF-01_office-exit.jpg`
- **运镜**：**固定 + 微推**（机位不动，极缓推入 3%）。⚠️ 不要用大运镜，AI 视频最易崩
- **中文提示词**
  > 电影感夜景，35mm 变形镜头，一个人背对镜头走出玻璃写字楼的旋转门，深色外套，单肩包。冷蓝紫色城市夜色，地面湿漉漉反着光，一盏暖黄路灯勾出他的肩线轮廓。浅景深，低照度低调光，胶片颗粒，街道空无一人。不要出现文字、Logo、商标，看不到脸。
- **English prompt**
  > Cinematic night shot, 35mm anamorphic. A lone figure seen from behind walks out of a glass office building's revolving door — dark jacket, shoulder bag. Cold blue-violet city night, wet reflective pavement, a single warm amber street lamp rimming his shoulders. Shallow depth of field, low-key lighting, film grain, empty street. No text, no logo, no brand marks, face not visible.
- **负面提示词**：`文字, 字幕, 水印, 商标, Logo, 正脸, 多人, 运动模糊, 畸变, 卡通, 3D渲染, 过曝`
- **生成参数**：5s / 16:9 / 1080p → 剪到 3.5s

---

### 镜 2 · 玻璃与暖光（3.5s）

- **首帧参考图**：`assets/video-refs/REF-02_glass.jpg`
- **运镜**：**横移**（左→右极缓，速度 ≈ 画面宽度 / 6s）
- **中文提示词**
  > 电影感夜景，50mm。从街上拍一家快餐店的大玻璃窗，店内暖黄色灯光透出来，玻璃上映出一个正要进门的模糊背影剪影。店外是冷蓝夜色，冷暖强对比。浅景深，胶片颗粒，安静孤独的氛围。不要出现可读文字、Logo、金色拱门、商标，不要出现人脸。
- **English prompt**
  > Cinematic night shot, 50mm. Exterior of a fast-food restaurant from the street — large glass window spilling warm amber interior light. A blurred back-view silhouette reflected in the glass, about to enter. Cold blue night outside, strong warm/cold contrast. Shallow depth of field, film grain, quiet lonely mood. No readable text, no logo, no golden arches, no brand marks, no faces.
- **负面提示词**：同镜 1，另加 `正脸, 招牌文字, 商标图形`
- **说明**：这是**目前 6 张参考图里最弱的一张**（构图偏满、玻璃反射感不够）。若追求更好效果，建议用上面的英文提示词重生成 2–3 版挑一张。

---

### 镜 3 · 一个人的餐盘（5.0s）⭐ 情绪最高点

- **首帧参考图**：`assets/video-refs/REF-03_meal.jpg`
- **运镜**：**缓推向下的俯角**（从 30° 俯角缓推到 40°，速度极慢）
- **中文提示词**
  > 电影感静物特写，微俯角，85mm。深色餐桌上摆着一个人的一顿饭：一个普通汉堡、一纸袋薯条、一杯插着吸管的饮料。暖黄顶光，热气微微升腾，背景很暗。桌子对面是一把空椅子，虚焦。浅景深，浓重阴影，胶片颗粒，安静的孤独感。不要出现文字、Logo、商标，不要出现人。
- **English prompt**
  > Cinematic still-life close-up, slightly overhead, 85mm. A single-person meal on a dark table: a plain burger, a paper sleeve of fries, a cup with a straw. Warm amber top light, faint steam, very dark background. An empty chair across the table, out of focus. Shallow depth of field, rich shadows, film grain, quiet loneliness. No text, no logo, no brand marks, no people.
- **负面提示词**：同镜 1，另加 `手, 人影, 多个餐盘`
- **关键**：**对面那把空椅子是这一镜的全部意义**。生成后检查空椅子是否"看得见"——看不见就重生成（可把提示词里的 `an empty chair` 提到句首加权）。

---

### 镜 4 · 光在桌面上亮起来（4.0s）⭐ 转折点

- **首帧参考图**：`assets/video-refs/REF-04_phone.jpg`
- **运镜**：**固定机位**，只让屏幕光自己变化（最稳，也最挑）
- **中文提示词**
  > 电影感特写，50mm 微距。深夜餐桌上一部手机正面朝上放在纸杯旁，屏幕刚刚亮起，把一小片温暖的琥珀色光投在木桌纹理上。屏幕内容是深色界面，模糊不可读。一只手的手指从画面右侧入镜。暖黄主光，环境冷色衰减，极浅景深，胶片颗粒，亲密的氛围。不要出现可读文字、Logo、商标、人脸。
- **English prompt**
  > Cinematic close-up, 50mm macro. A smartphone lies face-up on a dark restaurant table beside a paper cup, its screen just lighting up and casting a small pool of warm amber light across the wood grain. Screen content dark, blurred, unreadable. Fingers of one hand entering frame from the right. Warm amber key light, cold ambient falloff, very shallow depth of field, film grain, intimate mood. No readable text, no logo, no brand marks, no faces.
- **负面提示词**：同镜 1，另加 `可读文字, 界面截图, 手机品牌Logo`

> 🎬 **进阶做法（推荐，可信度最高）**：生成时让屏幕**内容完全不可读**，然后在剪映里用「跟踪 + 替换」把**我们的真实界面截图**贴到手机屏幕上。这样镜 4→镜 5 的过渡就有了物理依据：观众看到的是"同一个界面从手机里放大到全屏"。

---

### 镜 5 · 真实产品界面（7.0s）⭐ 全片唯一的"证据"

**这一镜不用 AI 生成**——用我们在 `assets/demo-video.mp4` 里已经有的真实界面截图，
在剪映里做**全屏推拉 + 三段瞬切**。AI 生成不出我们的 UI，硬做只会得到一坨假界面。

| 段 | 时间 | 画面 | 对应真实能力 |
| --- | --- | --- | --- |
| 5a | 00:16–00:18 | 开场第一句：它提起你上次点的那份 | `order-list` 真实历史订单 |
| 5b | 00:18–00:20.5 | 「麦辣鸡腿汉堡三件套，33 块 5」 | `query-meals` → `calculate-price` |
| 5c | 00:20.5–00:23 | 订单确认卡片：**待支付** / ¥33.5 / 堂食 / 支付时限 | `create-order` 真实建单 |

**素材来源**（三选一）
1. `assets/demo-video.mp4` 抽对应帧（`ffmpeg -ss <t> -i assets/demo-video.mp4 -frames:v 1`）
2. 重跑 `python tools/record_demo.py`，用 `demo_raw/01c_reply.png`、`02c_reply.png`、`03d_card.png`
3. 直接开页面临时截：`python -m server.main` → 浏览器截图

**后期做法**
- 每段**缓慢放大 8%**（模拟镜头推进），段间用 6 帧交叉溶解
- 5c 订单卡入场时加一个**轻微的琥珀色闪一下**（与镜 4 的屏幕光呼应）
- 界面保持原生的深色 `#12141a`，**不要加任何滤镜**——这一镜的任务是"真"，不是"美"

> ⚠️ 界面里的订单号是真实订单号，**上传公开平台前建议打码后 4 位**。

---

### 镜 6 · 他松下来了（3.5s）

- **首帧参考图**：`assets/video-refs/REF-05_profile.jpg`
- **运镜**：**固定 + 极缓推**（几乎不动，让表情自己发生）
- **中文提示词**
  > 电影感中近景夜景，85mm。一个年轻人的侧后四分之三视角，微微低着头看手里下方屏幕外的手机。屏幕的冷光勾出发际和面颊的一侧，餐厅的暖黄光填满另一侧。表情放松，嘴角有一个很浅的笑。半张脸在阴影里，侧向背对镜头，背景虚化很暗。浅景深，胶片颗粒，温柔安静的情绪。不要出现文字、Logo、商标。
- **English prompt**
  > Cinematic medium close-up, night, 85mm. A young person's three-quarter-back profile, head lowered, looking down at a phone held below frame. Cool screen light rims one side of the hair and cheek, warm amber restaurant light fills the other. Relaxed expression, a faint beginning of a smile. Half the face in shadow, mostly turned away from camera, very dark blurred background. Shallow depth of field, film grain, tender quiet mood. No text, no logo, no brand marks.
- **负面提示词**：同镜 1，另加 `正脸直视镜头, 大笑, 夸张表情`
- **⚠️ 注意**：这一张参考图**脸部比较清晰**。如果坚持 `BANNER.md` 的「无人脸」规范，把提示词改成只拍**手 + 屏幕光 + 下颌线**，或改拍**背影抬手**。两种都更安全，情绪损失很小。

---

### 镜 7 · 品牌卡（3.5s）

- **底图**：`assets/video-refs/REF-06_endcard-bg.jpg`（右侧大面积暗部正是留给文字的）
- **做法**：**不要用 AI 生成文字**。文字全部用剪映/代码后期叠加
- **画面层**
  1. 底图缓推 5%
  2. 左侧「光团子」吉祥物淡入（`assets/mascot.svg`，可让它呼吸式泛光）
  3. 标题「麦麦陪餐搭子」→ Slogan「一个人吃饭，但不孤单」依次淡入
  4. 底部 CTA：「完整实测演示 · github.com/jkjkiiiii/mcdinner-mate」
- **文字规格**（沿用 `BANNER.md` 已冻结的字号体系）

| 层 | 内容 | 字体 | 颜色 | 入场 |
| --- | --- | --- | --- | --- |
| 标题 | 麦麦陪餐搭子 | 微软雅黑 Bold | `#FFFCF5` | 00:26.5 淡入 |
| Slogan | 一个人吃饭，但不孤单 | 微软雅黑 Bold | `#FFCE7A` | 00:27.3 淡入（晚 0.8s） |
| 副标 | McDinnerMate · 基于麦当劳 MCP 的语音陪餐搭子 | 微软雅黑 Regular | `#AAB2C2` | 00:27.9 淡入 |
| CTA | ▶ 完整实测演示已开源 | 微软雅黑 Bold | `#FFCE7A` | 00:28.6 淡入，到 30s 保持 |

---

## 4. 声音设计

### 旁白（女声，温和不甜腻）

建议音色：`zh-CN-XiaoxiaoNeural`（与本项目 TTS 同源）或真人配音。
**语速放慢到 4.2–4.5 字/秒**，句子之间留 0.4s 以上呼吸。

| 时间 | 台词 | 字数 |
| --- | --- | --- |
| 00:03.5 | 晚上九点，又是一个人。 | 11 |
| 00:07.0 | 一个人吃饭，难的从来都不是饭。 | 15 |
| 00:10.5 | 是没人说话。 | 6 |
| 00:16.0 | 所以我们做了个饭搭子。 | 11 |
| 00:18.5 | 它记得你上次点了什么，报价一分不差。 | 18 |
| 00:23.0 | 帮你把单下好，陪你把这顿吃完。 | 15 |
| 00:27.0 | 一个人吃饭，但不孤单。 | 11 |

> 共 87 字 ≈ 19 秒语音，**留出 11 秒纯画面呼吸**。旁白塞满 30 秒是业余做法。

### 环境音效（决定"高级感"，别省）

| 时间 | 音效 |
| --- | --- |
| 00:00–00:04 | 夜风、脚步、远处车流；**没有音乐** |
| 00:03.5 | 一记很轻的玻璃门铃 |
| 00:07 | 音乐进入（淡入 1.5s） |
| 00:12 | 一声极轻的屏幕提示音（清理掉高频，要"闷"） |
| 00:16–00:23 | 轻微的键盘 / UI 音，音量在旁白之下 -18dB |
| 00:23 | 音乐副歌进来，暖度上升 |
| 00:27–00:30 | 收尾，尾音留 1s 自然衰减 |

### BGM 选型

- 调性：**钢琴 / 极简电子，大调但小音量**，60–72 BPM
- 不要：摇滚、鼓点强的、悲情弦乐（会变成"卖惨"）
- 参考方向：日系深夜食堂感、Lo-fi 钢琴、Ambient Pad
- ⚠️ **务必确认商用授权**。无预算就用平台曲库（剪映「音乐」页标注"可商用"的）

---

## 5. 三大 AI 视频站适配要点

| 平台 | 单镜时长 | 首尾帧 | 运镜控制 | 适配建议 |
| --- | --- | --- | --- | --- |
| **即梦（Dreamina）** | 5s / 10s | ✅ | ✅ 有运镜预设 | 中文提示词直接用；**首选**，图生视频质量稳 |
| **可灵（Kling）** | 5s / 10s | ✅ | ✅ | 中文提示词；人物/手部表现最好，镜 4 首选 |
| **海螺（MiniMax / Hailuo）** | 6s / 10s | ✅ | 一般 | 中文；镜头运动大胆，但需多生成几条挑 |
| **Vidu** | 4s / 8s | ✅ | 一般 | 中文；速度便宜，适合先用它试提示词 |
| **Sora / Runway / Pika** | 5–20s | 部分 | ✅ | 用英文提示词；画面最"电影"，但中文字形一律不要交给它 |

### 通用操作规范

1. **一律走「图生视频」**：把 `assets/video-refs/REF-0X.jpg` 当首帧上传，再填运镜 + 动态描述。
   纯文生视频画面会跳，且与参考图无关。
2. **比例先调到 16:9**（很多站默认 9:16），分辨率拉到 1080p。
3. **每镜生成 2–3 条**再挑——AI 视频一次成型概率约 1/3。
4. **运镜只写"轻"的**：缓推、横移、固定微动。写"环绕""快速跟拍"基本必崩。
5. **单镜时长取 5s 或 10s**，回剪映裁到目标时长；不够长就 0.9× 变速。

---

## 6. 剪映后期清单

- [ ] 新建 1920×1080 / 30fps 项目
- [ ] 按 §2 总表把 7 个镜头铺到时间轴，严格对时
- [ ] 镜 5 用真实截图，三段加 6 帧交叉溶解
- [ ] 统一调色：**高光偏暖黄（+琥珀）、阴影偏冷蓝紫**，整体压暗，对比 +8
      → 参数参考：色温 +6、色调 -3、对比 +8、高光 -10、阴影 +5、锐化 +10
- [ ] 全片加**统一胶片颗粒**（强度 15–20），避免"AI 干净感"穿帮
- [ ] 加**统一暗角**（vignette）收拢视线
- [ ] 旁白对齐时间轴，句子间至少留 0.4s
- [ ] 音效铺底，音乐在旁白处做 ducking（-6dB）
- [ ] 叠加字幕（位置：底部安全区上方 12%，字号 42–46，白色 + 30% 黑描边）
- [ ] 镜 5 订单号后 4 位打码
- [ ] 导出：H.264 / 1080p / 12–16 Mbps / AAC 192kbps

---

## 7. 参考图索引

| 文件 | 对应镜头 | 用途 | 备注 |
| --- | --- | --- | --- |
| `REF-01_office-exit.jpg` | 镜 1 | 首帧 | 背影走出写字楼，冷暖对比最强 |
| `REF-02_glass.jpg` | 镜 2 | 首帧 | ⚠️ 6 张里最弱，建议重生成 |
| `REF-03_meal.jpg` | 镜 3 | 首帧 | 空椅子是关键，检查是否可见 |
| `REF-04_phone.jpg` | 镜 4 | 首帧 | 屏幕光氛围到位，适合做屏幕替换底座 |
| `REF-05_profile.jpg` | 镜 6 | 首帧 | ⚠️ 脸部较清晰，若要严守"无人脸"需改拍局部 |
| `REF-06_endcard-bg.jpg` | 镜 7 | **底图**（非首帧） | 右侧暗部天然留白，直接叠文字 |

> 全部 6 张为 **1536×924**（原始 1536×1024，已裁掉底部 AI 水印），JPEG q92。
> 重生成为：`assets/video-refs/`，命名规则 `REF-0X_<英文短名>.jpg`。

### 复现/重生成这批参考图

参考图仅作**首帧与调性锚点**，不进入成片。若某张不满意，直接按 §3 对应镜头的
English prompt 在任意文生图站重生成即可，**不需要回到这里**。

---

## 8. 与 Demo 视频的接力关系

| | 本片（30s 宣传片） | `assets/demo-video.mp4`（73s Demo） |
| --- | --- | --- |
| 任务 | 让人**想看** | 让人**相信** |
| 画面 | AI 生成的氛围镜头 | 100% 真实界面截图 |
| 数据 | 一句「33 块 5」 | 每轮标注真实推理耗时 |
| 结尾 | CTA 指向 Demo 视频 / 仓库 | 品牌卡 + Star 引导 |

**发布顺序**：先发 30s 宣传片（各平台横版 + 竖版裁切），
评论区/简介第一条固定放 Demo 视频链接与仓库地址。

---

## 9. 开工 checklist

- [ ] 选平台（建议即梦或可灵起步）
- [ ] 6 张参考图下载到本地，检查是否满意（尤其 `REF-02`）
- [ ] 逐镜生成，每镜 2–3 条备选
- [ ] 镜 5 从 `demo_raw/` 或 Demo 视频抽帧，确认订单号打码
- [ ] 旁白录制（可用 `edge-tts` 试听定稿后再找人配，或直接用 TTS 出片）
- [ ] BGM 商用授权确认
- [ ] 剪映合成 → 导出 → 自查合规五条（§1）
