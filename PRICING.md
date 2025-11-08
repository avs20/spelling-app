# Hosting Platform Pricing Comparison

## 📊 Free Tier Comparison

| Platform | Free Tier | Limitations | Paid Plans Start |
|----------|-----------|-------------|------------------|
| **Fly.io** | 3 VMs (256MB each) | 160GB bandwidth/month | $1.94/month |
| **Railway** | $5 credit/month | ~500 hours runtime | $5/month |
| **Vercel** | Unlimited hobby | 100GB bandwidth | $20/month |
| **Render** | 750 hours/month | Sleeps after 15min | $7/month |
| **PythonAnywhere** | 1 web app | Limited CPU, 512MB storage | $5/month |
| **Cloudflare Pages** | Unlimited | 500 builds/month | $20/month |

---

## 🚀 Fly.io Pricing (Best Value ⭐)

### Free Tier (Hobby Plan)
- **3 shared-cpu-1x VMs** (256MB RAM each)
- **160GB bandwidth** per month
- **3GB persistent volume storage**
- **Always-on** (no cold starts)
- **HTTPS included**

**What You Can Run:**
- ✅ 3 small apps OR
- ✅ 1 app with 3 regions (global deployment) OR
- ✅ 1 app + 1 database + 1 cache

**Ideal for:** Small production apps, personal projects

### Paid Plans
| Plan | Price | RAM | vCPUs | Use Case |
|------|-------|-----|-------|----------|
| **shared-cpu-1x** | $1.94/mo | 256MB | 1 | Development |
| **shared-cpu-1x** | $5.70/mo | 1GB | 1 | Small apps |
| **shared-cpu-1x** | $11.31/mo | 2GB | 1 | Medium apps |
| **dedicated-cpu-1x** | $62/mo | 2GB | 1 | Production |
| **dedicated-cpu-2x** | $122/mo | 4GB | 2 | High traffic |

**Additional Costs:**
- Bandwidth: $0.02/GB (after 160GB free)
- Storage: $0.15/GB/month (after 3GB free)
- IPv4: $2/month (optional)

**Your Spelling App on Fly.io FREE:**
- 1 VM (256MB) = FREE
- 1GB storage = FREE (3GB included)
- ~50GB bandwidth/month = FREE
- **Total: $0/month** ✅

---

## 🚄 Railway Pricing

### Free Tier (Trial Plan)
- **$5 credit per month**
- **No credit card required**
- Usage: $0.000463 per GB-s
- ~**500 hours** of runtime with 512MB app

**After free credit runs out:**
- App pauses until next month
- OR upgrade to Hobby plan

### Paid Plans

#### Hobby Plan: $5/month
- **$5 included usage credit**
- Additional usage: $0.000463 per GB-s
- Up to **8GB RAM** per service
- Up to **32 vCPUs** per service
- **Unlimited** services
- **8 plugins** (databases, etc.)

#### Pro Plan: $20/month
- **$10 included usage credit**
- Priority support
- Everything in Hobby
- Dedicated Slack channel
- Team features

**Usage Calculation:**
```
Cost = Memory (GB) × Time (seconds) × $0.000463

Example (512MB app running 24/7):
0.5 GB × 2,592,000 seconds/month × $0.000463 = $600/month
(But $5 plan gives you $5 credit, so ~200 hours runtime)
```

**Your Spelling App on Railway:**
- With $5/month plan: ~200 hours runtime
- If app sleeps when idle: Probably stays within $5
- **Realistic cost: $5-10/month** after trial

---

## ⚡ Vercel Pricing

### Hobby Plan (FREE)
- **Unlimited** deployments
- **100GB bandwidth** per month
- **1000 serverless function** invocations/day
- **100 GB-hours** function execution
- **HTTPS** included
- **Auto-scaling**

**Limitations:**
- Serverless only (no persistent processes)
- 10-second function timeout
- 250MB deployment size
- No commercial use

### Pro Plan: $20/month per user
- **1TB bandwidth**
- **1,000,000** serverless invocations
- **1000 GB-hours** execution
- **60-second timeout**
- **Team collaboration**
- **Analytics**
- Commercial use allowed

### Enterprise: Custom pricing
- Custom limits
- SLA guarantees
- Dedicated support
- Advanced security

**Your Spelling App on Vercel:**
- Frontend: FREE ✅
- Backend: ⚠️ Not ideal (serverless, no SQLite)
- **Best used for frontend only**

---

## 🐌 Render Pricing

### Free Tier
- **750 hours** per month
- **512MB RAM**
- **0.1 CPU**
- Sleeps after **15 minutes** inactivity
- **100GB bandwidth**

**Limitations:**
- Slow cold starts (30+ seconds)
- No persistent disk (files deleted on restart)
- Single region only

### Paid Plans

#### Starter: $7/month
- **512MB RAM**
- **0.5 CPU**
- Always-on (no sleep)
- **100GB bandwidth**
- Persistent disk

#### Standard: $25/month
- **2GB RAM**
- **1 CPU**
- Always-on
- **100GB bandwidth**
- Persistent disk

#### Pro: $85/month
- **4GB RAM**
- **2 CPU**
- Everything else

**Your Spelling App on Render:**
- Free: Sleeps often, slow
- Starter ($7/mo): Better, but still slower than Fly.io
- **Not recommended**

---

## 🐍 PythonAnywhere Pricing

### Beginner (FREE)
- **1 web app** (yourname.pythonanywhere.com)
- **512MB storage**
- **3-month** app console access
- Limited CPU time (100 seconds/day)
- No always-on tasks

### Hacker: $5/month
- **2 web apps**
- **1GB storage**
- **Custom domain**
- More CPU time
- Always-on tasks

### Web Developer: $12/month
- **3 web apps**
- **2GB storage**
- More CPU and bandwidth

**Your Spelling App:**
- Free tier: Very limited, not ideal
- $5/month: Works but slow
- **Better options available**

---

## 🌐 Cloudflare Pages Pricing

### Free Tier
- **Unlimited** sites
- **Unlimited** requests
- **500 builds** per month
- **100GB/month** bandwidth
- **25,000 function invocations/month**

### Pro: $20/month
- Everything in Free
- **5,000 builds/month**
- **20,000,000 function invocations/month**

**Your Spelling App:**
- Frontend: Perfect ✅
- Backend: Use Cloudflare Workers ($5/mo for 10M requests)
- **Great for static sites**

---

## 💰 Real Cost Analysis

### Scenario 1: Hobby Project (Low Traffic)

| Platform | Monthly Cost | Performance | Recommendation |
|----------|--------------|-------------|----------------|
| **Fly.io** | **$0** | ⭐⭐⭐⭐⭐ | ✅ Best choice |
| Railway | $0 (trial) | ⭐⭐⭐⭐ | Good alternative |
| Vercel (frontend only) | $0 | ⭐⭐⭐⭐ | Static only |
| Render | $0 (slow) | ⭐⭐ | Not recommended |

**Winner: Fly.io** - Free, fast, always-on

---

### Scenario 2: Small Production (100-500 users/day)

| Platform | Monthly Cost | Traffic | Notes |
|----------|--------------|---------|-------|
| **Fly.io** | **$0-2** | 160GB | Still free! |
| Railway | $5-10 | Unlimited | Sleeps to save credit |
| Vercel | $20 | 1TB | Need Pro for commercial |
| Render | $7 | 100GB | Always-on |

**Winner: Fly.io** - Still free or ~$2/month

---

### Scenario 3: Growing App (1000+ users/day)

| Platform | Monthly Cost | Specs | Notes |
|----------|--------------|-------|-------|
| Fly.io | $5-15 | 1GB RAM | Scale as needed |
| Railway | $20+ | Team plan | Usage-based billing |
| Vercel | $20 | Pro plan | Frontend only |
| Render | $25 | 2GB RAM | Fixed pricing |

**Winner: Fly.io** - Pay only what you use

---

## 🎯 Pricing Breakdown for Your Spelling App

### Current Usage Estimate:
- **5-10 concurrent users**
- **~20GB bandwidth/month**
- **500MB storage** (database + images)
- **Always-on** requirement

### Option 1: Fly.io (Recommended)
```
Base: FREE ✅
- 1 VM (256MB): FREE (3 included)
- 500MB storage: FREE (3GB included)
- 20GB bandwidth: FREE (160GB included)

Total: $0/month
```

### Option 2: Railway
```
Trial: FREE for ~200 hours/month
After trial:
- Hobby plan: $5/month
- Estimated usage: ~$3/month
- With $5 credit: $2 additional

Total: $5-7/month
```

### Option 3: Vercel (Frontend) + Fly.io (Backend)
```
Frontend (Vercel): FREE
Backend (Fly.io): FREE

Total: $0/month ✅
```

### Option 4: Render
```
Free tier: $0 but slow (30s cold start)
Starter: $7/month for always-on

Total: $0 (slow) or $7/month
```

---

## 📈 Scaling Costs

### At 100 users/day:

| Platform | Cost | Performance |
|----------|------|-------------|
| Fly.io | $0 | ⭐⭐⭐⭐⭐ |
| Railway | $5/mo | ⭐⭐⭐⭐ |
| Vercel | $20/mo | ⭐⭐⭐⭐ |
| Render | $7/mo | ⭐⭐⭐ |

### At 1,000 users/day:

| Platform | Cost | Performance |
|----------|------|-------------|
| Fly.io | $5-10/mo | ⭐⭐⭐⭐⭐ |
| Railway | $20/mo | ⭐⭐⭐⭐ |
| Vercel | $20/mo | ⭐⭐⭐⭐ |
| Render | $25/mo | ⭐⭐⭐ |

### At 10,000 users/day:

| Platform | Cost | Performance |
|----------|------|-------------|
| Fly.io | $20-50/mo | ⭐⭐⭐⭐⭐ |
| Railway | $50-100/mo | ⭐⭐⭐⭐ |
| Vercel | $20/mo* | ⭐⭐⭐⭐ |
| Render | $85/mo | ⭐⭐⭐ |

*Vercel frontend only

---

## 🏆 Final Recommendation

### For Your Spelling App:

**Best Overall: Fly.io** 🥇
- **Cost:** $0/month (stays in free tier)
- **Performance:** Excellent (no cold starts)
- **Scaling:** Pay-as-you-grow
- **Total saved vs. paid plans:** $84-240/year

**Alternative: Railway** 🥈
- **Cost:** $5/month after trial
- **Performance:** Good
- **Ease:** Easiest deployment
- **Total cost:** $60/year

**For Frontend Only: Vercel** 🥉
- **Cost:** $0/month (hobby)
- **Performance:** Excellent for static files
- **Combine with Fly.io backend**

---

## 💡 Money-Saving Tips

### 1. Use Fly.io Free Tier Smart:
- Stay under 256MB RAM
- Keep bandwidth under 160GB
- Use 3GB storage efficiently
- **Savings: $84-240/year**

### 2. Optimize Images:
- Compress drawings (Phase 7 feature)
- Use WebP format
- Delete old drawings (keep last 10)
- **Saves bandwidth costs**

### 3. Cache Static Assets:
- Use CDN for frontend
- Cache API responses
- **Reduces compute time**

### 4. Split Services:
```
Frontend: Vercel/Cloudflare (FREE)
Backend: Fly.io (FREE)
Images: Cloudinary (25GB FREE)

Total: $0/month ✅
```

---

## 📊 Quick Decision Matrix

**Choose Fly.io if:**
- ✅ You want free + fast
- ✅ Need persistent storage
- ✅ Want always-on
- ✅ Plan to scale

**Choose Railway if:**
- ✅ Want easiest setup
- ✅ Okay with $5/month
- ✅ Need team features later
- ✅ Value simplicity

**Choose Vercel if:**
- ✅ Frontend only
- ✅ Want global CDN
- ✅ Need instant deploys
- ✅ Have backend elsewhere

**Avoid Render if:**
- ❌ Need fast cold starts
- ❌ Want free always-on
- ❌ Performance matters

---

## 🎯 Bottom Line

**For your Spelling App:** 

Go with **Fly.io** - it's:
- 💰 **FREE** (stays in free tier)
- ⚡ **FAST** (~500ms response)
- 🌍 **GLOBAL** (edge deployment)
- 📈 **SCALABLE** (pay only when needed)

**Deploy command:**
```bash
flyctl launch
flyctl volumes create data_volume --size 1
flyctl deploy
```

**Monthly cost: $0** 🎉

**Potential future cost at 10,000 users/day: $20-50/month**
(Still cheaper than other platforms!)
