import handler from 'serve-handler';
import http from 'http';

const port = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  return handler(req, res, {
    public: 'dist',
    rewrites: [{ source: '**', destination: '/index.html' }]
  });
});

server.listen(port, () => {
  console.log(`Running on port ${port}`);
});
