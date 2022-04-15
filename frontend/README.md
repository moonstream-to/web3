This is a [bugout-dev](https://github.com/bugout-dev) frontend app template ment to be bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Creating new app

1. `npx create-next-app app-name -e https://github.com/bugout-dev/frontend_template`
2. `cd app-name`
3. `cp sample.env my.env` and setup variables
4.  `source my.env`
5.  Modify `src/core/constants.js` to configure app constants 

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `pages/index.js`. The page auto-updates as you edit the file.

For each page url page you need to create a file in `/pages` directory. See examples in `/pages_templates`


NEXT js app can be used with SSR - [API routes](https://nextjs.org/docs/api-routes/introduction) can be accessed on [http://localhost:3000/api/hello](http://localhost:3000/api/hello). This endpoint can be edited in `pages/api/hello.tsx`.

The `pages/api` directory is mapped to `/api/*`. Files in this directory are treated as [API routes](https://nextjs.org/docs/api-routes/introduction) instead of React pages.

## Learn More

To learn more about Bugout and Moonstream, take a look at the following resources:
- [Moonstream.to Documentation](https://moonstream.to/docs) - learn about Moonstream.to features and API.

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!

## Deploy on Static bucket AWS

First lint your files. Happy linter - happy life! 
```bash
yarn lint
```
Next
```bash
yarn build
```
Your project will be generated in `/build` directory

Since you might have dynamic routes that have no physical index.html that will correspond to your route, your routes will eventually be handled by s3 error redirect. 
In order to display dynamic routes correctly, set S3 404 redirect to `/base_url/entry-point/index.html` This route will ensure correct load and entrying in the next js app

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.
