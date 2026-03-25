/**
 * E-008: Contract Detail — F031, F035, F063
 * Vizualizare contract cu:
 *  - Semnare → auto-creare Proiect PM (F063)
 *  - Navigare cross-modul: Contact, Ofertă, Proiect
 */
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Steps,
  Spin,
  Alert,
  Divider,
  message,
  Modal,
  Input,
} from "antd";
import {
  ArrowLeftOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  UserOutlined,
  ProjectOutlined,
  StopOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons";
import { useState } from "react";
import { pipelineService } from "../services/pipelineService";
import { contactService } from "../../../services/contactService";
import type { Contract } from "../../../types";

const { Title, Text } = Typography;
const { TextArea } = Input;

const STATUS_CONFIG: Record<
  string,
  { color: string; label: string; step: number }
> = {
  draft: { color: "default", label: "Draft", step: 0 },
  pending_approval: { color: "processing", label: "Aprobare", step: 1 },
  approved: { color: "cyan", label: "Aprobat", step: 2 },
  sent: { color: "blue", label: "Trimis", step: 3 },
  negotiation: { color: "orange", label: "Negociere", step: 4 },
  signed: { color: "green", label: "Semnat", step: 5 },
  active: { color: "green", label: "Activ", step: 5 },
  completed: { color: "purple", label: "Finalizat", step: 6 },
  terminated: { color: "red", label: "Reziliat", step: 6 },
};

const PIPELINE_STEPS = [
  { title: "Draft" },
  { title: "Aprobare" },
  { title: "Aprobat" },
  { title: "Trimis" },
  { title: "Negociere" },
  { title: "Semnat" },
  { title: "Finalizat" },
];

function fmtDate(d?: string | null): string {
  if (!d) return "—";
  return new Date(d).toLocaleDateString("ro-RO");
}

export default function ContractDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [terminateOpen, setTerminateOpen] = useState(false);
  const [terminateReason, setTerminateReason] = useState("");
  const [signing, setSigning] = useState(false);

  // Fetch contract
  const {
    data: contractData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["contract", id],
    queryFn: () => pipelineService.getContract(id!),
    enabled: !!id,
  });

  const contract: Contract | undefined = contractData?.data;

  // Fetch linked contact
  const { data: contactData } = useQuery({
    queryKey: ["contact", contract?.contact_id],
    queryFn: () => contactService.get(contract!.contact_id),
    enabled: !!contract?.contact_id,
  });

  const contact = contactData?.data;

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !contract) {
    return (
      <Alert
        type="error"
        message="Contract negăsit"
        description="Contractul solicitat nu a fost găsit."
        showIcon
        action={
          <Button onClick={() => navigate(-1)}>Înapoi</Button>
        }
      />
    );
  }

  const statusCfg = STATUS_CONFIG[contract.status] ?? STATUS_CONFIG.draft!;
  const canSign = ["approved", "sent", "negotiation"].includes(contract.status);
  const canTerminate = ["signed", "active"].includes(contract.status);
  const hasProject = !!contract.project_id;

  // F063: Sign → auto-create PM project
  const handleSign = async () => {
    setSigning(true);
    try {
      const res = await pipelineService.signContract(id!);
      message.success("Contract semnat! Proiect PM creat automat (F063).");
      queryClient.invalidateQueries({ queryKey: ["contract", id] });

      // Navigate to the auto-created project if returned
      if (res.data.project_id) {
        Modal.confirm({
          title: "Proiect creat automat",
          icon: <CheckCircleOutlined style={{ color: "#52c41a" }} />,
          content:
            "Contractul a fost semnat și un proiect PM a fost creat automat. Dorești să navighezi la proiect?",
          okText: "Mergi la Proiect",
          cancelText: "Rămâi aici",
          onOk: () => navigate(`/pm/projects/${res.data.project_id}/gantt`),
        });
      }
    } catch {
      message.error("Eroare la semnarea contractului");
    } finally {
      setSigning(false);
    }
  };

  // F035: Terminate contract
  const handleTerminate = async () => {
    try {
      await pipelineService.terminateContract(id!, terminateReason);
      message.success("Contract reziliat.");
      setTerminateOpen(false);
      queryClient.invalidateQueries({ queryKey: ["contract", id] });
    } catch {
      message.error("Eroare la rezilierea contractului");
    }
  };

  return (
    <div>
      {/* Navigation */}
      <Space style={{ marginBottom: 16 }} wrap>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
        >
          Înapoi
        </Button>
        {contract.contact_id && (
          <Button
            icon={<UserOutlined />}
            onClick={() => navigate(`/crm/contacts/${contract.contact_id}`)}
          >
            Contact
          </Button>
        )}
        {contract.offer_id && (
          <Button
            icon={<FileTextOutlined />}
            onClick={() =>
              navigate(`/pipeline/offers/${contract.offer_id}`)
            }
          >
            Ofertă
          </Button>
        )}
        {contract.opportunity_id && (
          <Button
            onClick={() =>
              navigate(
                `/pipeline/opportunities/${contract.opportunity_id}`
              )
            }
          >
            Oportunitate
          </Button>
        )}
        {hasProject && (
          <Button
            type="primary"
            icon={<ProjectOutlined />}
            onClick={() =>
              navigate(`/pm/projects/${contract.project_id}/gantt`)
            }
          >
            Proiect PM
          </Button>
        )}
      </Space>

      {/* Status pipeline */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Steps
          current={statusCfg.step}
          status={
            contract.status === "terminated" ? "error" : undefined
          }
          items={PIPELINE_STEPS}
          size="small"
        />
      </Card>

      {/* Header */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Title level={4} style={{ margin: 0 }}>
                {contract.title}
              </Title>
              <Tag color={statusCfg.color}>{statusCfg.label}</Tag>
              <Text type="secondary">#{contract.contract_number}</Text>
            </Space>
          </Col>
          <Col>
            <Space>
              {canSign && (
                <Button
                  type="primary"
                  icon={<CheckCircleOutlined />}
                  loading={signing}
                  onClick={handleSign}
                >
                  Semnează Contract → Creare Proiect (F063)
                </Button>
              )}
              {canTerminate && (
                <Button
                  danger
                  icon={<StopOutlined />}
                  onClick={() => setTerminateOpen(true)}
                >
                  Reziliază
                </Button>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Cross-module info banner */}
      {hasProject && (
        <Alert
          type="success"
          message="Proiect PM creat automat din contract (F063)"
          description={
            <Button
              type="link"
              icon={<ProjectOutlined />}
              onClick={() =>
                navigate(`/pm/projects/${contract.project_id}/gantt`)
              }
            >
              Deschide Proiect →
            </Button>
          }
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={16}>
        <Col xs={24} lg={16}>
          {/* Details */}
          <Card
            title="Detalii Contract"
            style={{ marginBottom: 16 }}
          >
            <Descriptions column={{ xs: 1, sm: 2 }} bordered size="small">
              <Descriptions.Item label="Client">
                {contact ? (
                  <a
                    onClick={() =>
                      navigate(`/crm/contacts/${contract.contact_id}`)
                    }
                  >
                    {contact.company_name}
                  </a>
                ) : (
                  contract.contact_id
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Nr. Contract">
                {contract.contract_number}
              </Descriptions.Item>
              <Descriptions.Item label="Data Început">
                {fmtDate(contract.start_date)}
              </Descriptions.Item>
              <Descriptions.Item label="Data Sfârșit">
                {fmtDate(contract.end_date)}
              </Descriptions.Item>
              <Descriptions.Item label="Data Semnare">
                {fmtDate(contract.signed_date)}
              </Descriptions.Item>
              <Descriptions.Item label="Ofertă sursă">
                {contract.offer_id ? (
                  <a
                    onClick={() =>
                      navigate(`/pipeline/offers/${contract.offer_id}`)
                    }
                  >
                    Vezi ofertă
                  </a>
                ) : (
                  "—"
                )}
              </Descriptions.Item>
              {contract.description && (
                <Descriptions.Item label="Descriere" span={2}>
                  {contract.description}
                </Descriptions.Item>
              )}
              {contract.terms_and_conditions && (
                <Descriptions.Item label="Termeni" span={2}>
                  {contract.terms_and_conditions}
                </Descriptions.Item>
              )}
              {contract.notes && (
                <Descriptions.Item label="Note" span={2}>
                  {contract.notes}
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          {/* Financial */}
          <Card title="Financiar" style={{ marginBottom: 16 }}>
            <Statistic
              title="Valoare Contract"
              value={contract.total_value}
              prefix={contract.currency}
              precision={0}
            />
          </Card>

          {/* Cross-module links */}
          <Card title="Navigare Cross-Modul">
            <Space direction="vertical" style={{ width: "100%" }}>
              <Divider orientation="left" orientationMargin={0} style={{ fontSize: 12, margin: "4px 0" }}>
                Flux P1 End-to-End
              </Divider>
              <Button
                block
                icon={<UserOutlined />}
                onClick={() =>
                  navigate(`/crm/contacts/${contract.contact_id}`)
                }
              >
                1. Client (CRM)
              </Button>
              {contract.opportunity_id && (
                <Button
                  block
                  onClick={() =>
                    navigate(
                      `/pipeline/opportunities/${contract.opportunity_id}`
                    )
                  }
                >
                  2. Oportunitate (Pipeline)
                </Button>
              )}
              {contract.offer_id && (
                <Button
                  block
                  icon={<FileTextOutlined />}
                  onClick={() =>
                    navigate(`/pipeline/offers/${contract.offer_id}`)
                  }
                >
                  3. Ofertă (Pipeline)
                </Button>
              )}
              <Button
                block
                type="dashed"
                disabled
              >
                4. Contract (actual)
              </Button>
              {hasProject ? (
                <Button
                  block
                  type="primary"
                  icon={<ProjectOutlined />}
                  onClick={() =>
                    navigate(
                      `/pm/projects/${contract.project_id}/gantt`
                    )
                  }
                >
                  5. Proiect PM → Execuție
                </Button>
              ) : canSign ? (
                <Button
                  block
                  type="dashed"
                  icon={<ExclamationCircleOutlined />}
                  onClick={handleSign}
                  loading={signing}
                >
                  5. Semnează → Creare Proiect
                </Button>
              ) : (
                <Button block disabled>
                  5. Proiect (necesită semnare)
                </Button>
              )}
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Terminate modal */}
      <Modal
        title="Reziliere Contract"
        open={terminateOpen}
        onOk={handleTerminate}
        onCancel={() => setTerminateOpen(false)}
        okText="Reziliază"
        okButtonProps={{ danger: true }}
      >
        <p>Motivul rezilierii:</p>
        <TextArea
          rows={3}
          value={terminateReason}
          onChange={(e) => setTerminateReason(e.target.value)}
          placeholder="Descrieți motivul rezilierii..."
        />
      </Modal>
    </div>
  );
}
