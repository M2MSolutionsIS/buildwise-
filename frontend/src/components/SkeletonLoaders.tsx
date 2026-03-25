/**
 * C-004: Skeleton Loader — Shimmer effects for: card, row, KPI.
 * Common (P1+P2+P3).
 */
import { Skeleton, Card, Row, Col, Space } from "antd";

/** Skeleton for a standard data card */
export function SkeletonCard({ count = 1 }: { count?: number }) {
  return (
    <Row gutter={[16, 16]}>
      {Array.from({ length: count }).map((_, i) => (
        <Col xs={24} sm={12} md={8} lg={6} key={i}>
          <Card size="small">
            <Skeleton active paragraph={{ rows: 2 }} />
          </Card>
        </Col>
      ))}
    </Row>
  );
}

/** Skeleton for table rows */
export function SkeletonRows({ rows = 5 }: { rows?: number }) {
  return (
    <div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ padding: "12px 0", borderBottom: "1px solid #f0f0f0" }}>
          <Skeleton active title={false} paragraph={{ rows: 1, width: `${60 + Math.random() * 30}%` }} />
        </div>
      ))}
    </div>
  );
}

/** Skeleton for KPI cards (summary stats) */
export function SkeletonKPI({ count = 4 }: { count?: number }) {
  return (
    <Row gutter={16}>
      {Array.from({ length: count }).map((_, i) => (
        <Col xs={12} md={24 / count} key={i}>
          <Card size="small">
            <Space direction="vertical" size={4} style={{ width: "100%" }}>
              <Skeleton.Input active size="small" style={{ width: 80, height: 14 }} />
              <Skeleton.Input active size="large" style={{ width: 120, height: 28 }} />
            </Space>
          </Card>
        </Col>
      ))}
    </Row>
  );
}

/** Skeleton for a full page layout (header + KPIs + table) */
export function SkeletonPage() {
  return (
    <div style={{ padding: 24 }}>
      <Skeleton active title={{ width: 200 }} paragraph={false} style={{ marginBottom: 24 }} />
      <SkeletonKPI count={4} />
      <div style={{ marginTop: 24 }}>
        <Card>
          <SkeletonRows rows={8} />
        </Card>
      </div>
    </div>
  );
}
