import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { message } from "antd";
import { offerService, type OfferFilters } from "../services/offerService";
import type { OfferCreate, OfferUpdate } from "../../../types";

export function useOffers(filters: OfferFilters = {}) {
  return useQuery({
    queryKey: ["offers", filters],
    queryFn: () => offerService.list(filters),
  });
}

export function useOffer(id: string | undefined) {
  return useQuery({
    queryKey: ["offer", id],
    queryFn: () => offerService.get(id!),
    enabled: !!id,
  });
}

export function useOfferVersions(id: string | undefined) {
  return useQuery({
    queryKey: ["offer-versions", id],
    queryFn: () => offerService.listVersions(id!),
    enabled: !!id,
  });
}

export function useCreateOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: OfferCreate) => offerService.create(payload),
    onSuccess: () => {
      message.success("Ofertă creată cu succes.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la crearea ofertei."),
  });
}

export function useUpdateOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: OfferUpdate }) =>
      offerService.update(id, payload),
    onSuccess: () => {
      message.success("Ofertă actualizată.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
      queryClient.invalidateQueries({ queryKey: ["offer"] });
    },
    onError: () => message.error("Eroare la actualizare."),
  });
}

export function useDeleteOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: offerService.delete,
    onSuccess: () => {
      message.success("Ofertă ștearsă.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la ștergere."),
  });
}

export function useSubmitOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => offerService.submit(id),
    onSuccess: () => {
      message.success("Ofertă trimisă pentru aprobare.");
      queryClient.invalidateQueries({ queryKey: ["offer"] });
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la trimitere."),
  });
}

export function useCreateOfferVersion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => offerService.createVersion(id),
    onSuccess: () => {
      message.success("Versiune nouă creată.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
      queryClient.invalidateQueries({ queryKey: ["offer-versions"] });
    },
    onError: () => message.error("Eroare la creare versiune."),
  });
}

export function useSendOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => offerService.send(id),
    onSuccess: () => {
      message.success("Ofertă trimisă clientului.");
      queryClient.invalidateQueries({ queryKey: ["offer"] });
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la trimitere."),
  });
}

export function useApproveOffer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: { approved: boolean; comment?: string } }) =>
      offerService.approve(id, decision),
    onSuccess: (_, vars) => {
      message.success(vars.decision.approved ? "Ofertă aprobată." : "Ofertă respinsă.");
      queryClient.invalidateQueries({ queryKey: ["offer"] });
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la procesare."),
  });
}

export function useUpdateOfferStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status, reason }: { id: string; status: string; reason?: string }) =>
      offerService.updateStatus(id, status, reason),
    onSuccess: () => {
      message.success("Status actualizat.");
      queryClient.invalidateQueries({ queryKey: ["offer"] });
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la actualizare status."),
  });
}
