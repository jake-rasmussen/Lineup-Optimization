# Lineup-Optimization

This is a research project within the **Sports Analytics Research Group** at **Johns Hopkins University**. The goal is to develop a web-based tool for optimizing baseball batting lineups using advanced statistical analysis and optimization algorithms.

## Features

- **Historical Data Integration**: Incorporates historical baseball statistics to inform lineup optimization.
- **Linear Weights Methodology**: Uses advanced statistical techniques to evaluate player contributions.
- **Optimization Algorithms**: Implements modern computational methods to maximize expected run production.
- **User Constraints**: Allows users to define lineup constraints for real-world applications.

## Tech Stack

This project is built with the **T3 Stack** and utilizes **Supabase** for authentication and database management.

- [Next.js](https://nextjs.org)
- [tRPC](https://trpc.io)
- [TypeScript](https://www.typescriptlang.org)
- [Prisma](https://prisma.io)
- [PostgreSQL](https://www.postgresql.org)
- [TailwindCSS](https://tailwindcss.com)
- [Supabase](https://supabase.com)

## Getting Started

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/Lineup-Optimization.git
cd Lineup-Optimization
yarn
```

### Running the Web App

Start the web app:

```bash
cd web-app
yarn dev  # or npm run dev
```

### Running the Development Server

Start the development server:

```bash
cd web-server
py -m uvicorn main:app --reload
```