// 岗位数据存储
// 以后可以直接在这个文件里手动增加更多岗位，不需要数据库

export interface Job {
  id: string;
  title: string;
  company: string;
  salary: string;
  description: string; // 职责和要求
}

export const JOBS: Job[] = [
  {
    id: "1",
    title: "Java开发工程师",
    company: "阿里巴巴集团",
    salary: "20K-35K",
    description: "职责：负责后端服务开发，参与核心业务系统设计与实现。要求：本科及以上学历，计算机相关专业，熟悉Java、Spring框架，有微服务开发经验，了解分布式系统设计。"
  },
  {
    id: "2",
    title: "产品经理",
    company: "腾讯科技",
    salary: "18K-30K",
    description: "职责：负责产品规划、需求分析、用户体验优化。要求：本科及以上学历，有产品思维，熟悉互联网产品设计流程，具备良好的沟通协调能力，有数据分析能力。"
  },
  {
    id: "3",
    title: "内容运营",
    company: "字节跳动",
    salary: "12K-22K",
    description: "职责：负责内容策划、用户运营、活动策划执行。要求：本科及以上学历，对内容敏感，有新媒体运营经验，熟悉短视频平台，具备创意策划能力，数据驱动思维。"
  },
  {
    id: "4",
    title: "前端开发工程师",
    company: "美团",
    salary: "16K-28K",
    description: "职责：负责前端页面开发，优化用户体验，参与技术方案设计。要求：本科及以上学历，熟悉React/Vue等前端框架，了解TypeScript，有移动端开发经验，关注前端新技术。"
  },
  {
    id: "5",
    title: "数据分析师",
    company: "滴滴出行",
    salary: "15K-25K",
    description: "职责：负责业务数据分析、数据报表搭建、数据挖掘。要求：本科及以上学历，统计学/数学/计算机相关专业，熟悉SQL、Python，有数据分析经验，逻辑思维清晰，对数据敏感。"
  }
];
